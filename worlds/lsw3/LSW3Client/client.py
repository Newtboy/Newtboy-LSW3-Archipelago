import warnings

warnings.filterwarnings(
    "ignore",
    message="_speedups not available.*",
    module="NetUtils"
)

warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API.*",
    module="ModuleUpdate"
)

warnings.filterwarnings("ignore", category=UserWarning)


import asyncio
import logging

from CommonClient import (
    CommonContext,
    get_base_parser,
    server_loop,
    gui_enabled
)

from .game import LSW3Memory

from worlds.lsw3.Items import (
    ITEM_GOLD_BRICK,
    CHARACTER_ITEM_IDS,
    RED_BRICK_ITEM_IDS,
    ITEM_STUDS_10,
    ITEM_STUDS_100,
    ITEM_STUDS_1000,
    ITEM_STUDS_10000
)

from worlds.lsw3.Locations import (
    RED_BRICK_LOCATION_IDS,
    CHARACTER_LOCATION_IDS
)


class LSW3Context(CommonContext):
    game = "LEGO Star Wars III: The Clone Wars"
    items_handling = 0b111
    goal_sent = False

    def __init__(self, server_address, password):
        super().__init__(server_address, password)

        self.game_memory = None

        # =========================================================
        # Character configuration
        # =========================================================

        # Characters that can be obtained directly by purchasing
        # them in one of the hubs/ships.
        #
        # These have a special case when received from AP:
        # if AP gives the character before the player buys it,
        # the character's own location is immediately checked so
        # the character item cannot become self-locked.
        #
        # Names MUST match LSW3Memory.CHARACTERS exactly.
        self.hub_characters = {
            "Cad Bane",
            "Count Dooku",
            "Admiral Yularen",
            "Jango Fett",
            "R4-P17",
            "Neimoidian",
            "Battle Droid",
            "Super Battle Droid",
            "Gonk Droid",
            "LEP Servant Droid",
            "Gold Super Battle Droid",
            "Droideka",
            "Captain Typho",
            "Queen Neeyutnee",
            "Battle Droid Commander",
            "Hondo Ohnaka",
            "Pirate Ruffian",
            "Senator Kharrus",
            "Tee Watt Kaa",
            "Turk Falso",
            "Probe Droid",
            "Lurmen Villager",
            "TX-20",
            "Geonosian Guard",
            "Workout Clone Trooper",
            "Bib Fortuna",
            "Undead Geonosian",
            "Heavy Super Battle Droid",
            "R6-H5",
            "Clone Pilot",
            "MSE-6",
            "Sionver Boll",
            "Bail Organa",
            "Luxury Droid",
            "Onaconda Farr",
            "Senator Philo",
            "Senate Commando (Captain)",
            "Senate Commando",
            "Gamorrean Guard",
            "General Grievous",
        }

        # NOTE:
        # "Destroyer Droid" is listed as a hub character in the
        # supplied unlock list, but it is NOT currently present
        # in lsw3_data_pointers.CHARACTERS.
        #
        # It should be added here after its memory pointer is found.
        #
        # "Siover Boll" and "Onaconda Farr" use the spellings from
        # the actual character pointer table.

        # =========================================================
        # Red Brick state
        # =========================================================

        self.archi_red_bricks = set()
        self.expected_red_bricks = set()

        self.randomized_red_bricks = set()
        self.nonrandomized_red_bricks = set()

        self.previous_1_8 = 0
        self.previous_9_16 = 0
        self.previous_17_18 = 0

        # =========================================================
        # Character state
        # =========================================================

        # Filled after Dolphin connects.
        #
        # Each character has three pieces of state:
        #
        #   ap_received:
        #       Archipelago has actually given us this character.
        #
        #   bought:
        #       The base game has naturally unlocked this character.
        #       This includes mission/minikit/etc. unlocks, not
        #       necessarily literally buying the character.
        #
        #   location_checked:
        #       The character's AP location has already been sent.
        #
        # This gives us the complete state machine:
        #
        #   False, False -> nothing
        #   False, True  -> check location, keep locked
        #   True,  False -> unlock character
        #   True,  True  -> unlock character, location checked
        #
        self.character_state = {}

        self.goal_sent = False

    # =============================================================
    # GUI
    # =============================================================

    def run_gui(self):
        from kvui import GameManager

        class LSW3Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]

            base_title = "Archipelago LEGO Star Wars III Client"

        self.ui = LSW3Manager(self)

        self.ui_task = asyncio.create_task(
            self.ui.async_run(),
            name="UI"
        )

    # =============================================================
    # Connection
    # =============================================================

    async def server_auth(self, password_requested=False):
        await super().server_auth(password_requested)

        if self.game_memory is None:
            print("Connecting to Dolphin...")

            try:
                self.game_memory = LSW3Memory()
                print("Connected to Dolphin!")

                # Initialize character state now that we know the
                # actual character list from LSW3Memory.
                self.character_state = {
                    character: {
                        "ap_received": False,
                        "bought": False,
                        "location_checked": False,
                    }
                    for character in self.game_memory.CHARACTERS
                }

                # Initialize red-brick watcher state.
                self.previous_1_8 = self.game_memory.red_bricks_1_8
                self.previous_9_16 = self.game_memory.red_bricks_9_16
                self.previous_17_18 = self.game_memory.red_bricks_17_18

                asyncio.create_task(self.game_watcher())

            except RuntimeError as e:
                print(f"WARNING: {e}")

        await self.get_username()
        await self.send_connect()

    # =============================================================
    # Game watcher
    # =============================================================

    async def game_watcher(self):
        while True:
            await self.check_red_bricks()
            await self.check_characters()

            await asyncio.sleep(0.1)

    # =============================================================
    # Characters
    # =============================================================

    async def check_characters(self):
        """
        Synchronize character state between the game and AP.

        The important distinction is:

            game_unlocked != AP_owned

        A character naturally unlocked by the game becomes a
        LocationCheck, but does NOT become AP-owned.

        A character received from AP becomes AP-owned and remains
        unlocked regardless of whether the player has naturally
        obtained it.
        """

        for character in self.game_memory.CHARACTERS:
            state = self.character_state[character]

            ap_received = state["ap_received"]
            bought = state["bought"]
            location_checked = state["location_checked"]

            is_unlocked = self.game_memory.character_unlocked(character)

            # -----------------------------------------------------
            # Detect a natural game unlock.
            # -----------------------------------------------------
            #
            # If AP does not own the character, any unlock detected
            # in memory is the player obtaining the character through
            # normal game progression.
            #
            if is_unlocked and not ap_received:
                state["bought"] = True
                bought = True

            # -----------------------------------------------------
            # AP owns the character.
            # -----------------------------------------------------
            #
            # AP ownership always wins. If something in the game
            # causes the character to become locked, restore it.
            #
            if ap_received:
                if not is_unlocked:
                    self.game_memory.unlock_character(character)

            # -----------------------------------------------------
            # Player naturally obtained the character.
            # -----------------------------------------------------
            #
            # This is an AP location check, NOT an AP item receipt.
            #
            # After checking the location, lock the character again
            # unless AP has separately given us the character.
            #
            elif bought:
                if not location_checked:
                    await self.character_collected(character)
                    state["location_checked"] = True

                self.game_memory.lock_character(character)

    async def character_collected(self, character):
        """
        Report a naturally obtained character as an AP location.
        """

        print(f"Detected physical unlock of {character}")

        location_name = f"Character Unlock: {character}"
        location_id = CHARACTER_LOCATION_IDS[location_name]

        await self.send_msgs([{
            "cmd": "LocationChecks",
            "locations": [location_id],
        }])

    async def receive_character(self, character):
        """
        Give a character to the player from Archipelago.
        """

        if character not in self.character_state:
            print(
                f"WARNING: Received unknown character "
                f"{character}"
            )
            return

        state = self.character_state[character]

        # ---------------------------------------------------------
        # AP owns the character.
        # ---------------------------------------------------------

        state["ap_received"] = True

        # Give the character immediately.
        self.game_memory.unlock_character(character)

        print(
            f"Received character from Archipelago: "
            f"{character}"
        )

        # ---------------------------------------------------------
        # Hub character special case.
        # ---------------------------------------------------------
        #
        # If this character can normally be bought directly in the
        # hub, receiving it from AP before buying it would otherwise
        # make its own location inaccessible.
        #
        # Therefore:
        #
        #   AP gives character
        #       ↓
        #   unlock character
        #       ↓
        #   check character location
        #
        # We do NOT mark "bought" here. AP receiving the character
        # is not the same thing as the player naturally obtaining it.
        #
        if (
            character in self.hub_characters
            and not state["bought"]
            and not state["location_checked"]
        ):
            print(
                f"{character} is a hub character. "
                f"Checking its associated location."
            )

            await self.character_collected(character)

            state["location_checked"] = True

    # =============================================================
    # Red Bricks
    # =============================================================

    async def check_red_bricks(self):
        current_1_8 = self.game_memory.red_bricks_1_8
        current_9_16 = self.game_memory.red_bricks_9_16
        current_17_18 = self.game_memory.red_bricks_17_18

        # ---------------------------------------------------------
        # Red Bricks 1-8
        # ---------------------------------------------------------

        for brick_number in range(1, 9):
            bit = 1 << (brick_number - 1)

            was_unlocked = self.previous_1_8 & bit
            is_unlocked = current_1_8 & bit

            if not was_unlocked and is_unlocked:
                await self.red_brick_collected(brick_number)

        # ---------------------------------------------------------
        # Red Bricks 9-16
        # ---------------------------------------------------------

        for brick_number in range(9, 17):
            bit = 1 << (brick_number - 9)

            was_unlocked = self.previous_9_16 & bit
            is_unlocked = current_9_16 & bit

            if not was_unlocked and is_unlocked:
                await self.red_brick_collected(brick_number)

        # ---------------------------------------------------------
        # Red Bricks 17-18
        # ---------------------------------------------------------

        for brick_number in range(17, 19):
            bit = 1 << (brick_number - 17)

            was_unlocked = self.previous_17_18 & bit
            is_unlocked = current_17_18 & bit

            if not was_unlocked and is_unlocked:
                await self.red_brick_collected(brick_number)

        # Save current state for the next watcher iteration.
        self.previous_1_8 = current_1_8
        self.previous_9_16 = current_9_16
        self.previous_17_18 = current_17_18

        # ---------------------------------------------------------
        # Goal
        # ---------------------------------------------------------

        if (
            not self.goal_sent
            and self.game_memory.all_red_bricks_unlocked()
        ):
            print("All 18 Red Bricks collected! Game complete.")

            await self.send_msgs([{
                "cmd": "StatusUpdate",
                "status": 30,  # CLIENT_GOAL
            }])

            self.goal_sent = True

    async def red_brick_collected(self, brick_number):
        name = f"Red Brick {brick_number}"

        # ---------------------------------------------------------
        # AP caused this brick to appear.
        # ---------------------------------------------------------

        if brick_number in self.expected_red_bricks:
            print(
                f"{name} appeared because Archipelago gave it to us."
            )

            self.expected_red_bricks.remove(brick_number)

            # Don't let the game count the AP-granted brick
            # as a physical collection.
            self.game_memory.lock_red_brick_count(brick_number)

            return

        # ---------------------------------------------------------
        # Player physically collected it.
        # ---------------------------------------------------------

        print(f"Detected physical collection of {name}")

        # This brick is not randomized.
        if brick_number not in self.randomized_red_bricks:
            print(
                f"{name} is not randomized. "
                f"Leaving it alone."
            )
            return

        # This brick is randomized, so report the location.
        print(
            f"{name} is randomized. "
            f"Sending location check."
        )

        location_name = f"Red Brick Location {brick_number}"
        location_id = RED_BRICK_LOCATION_IDS[location_name]

        await self.send_msgs([{
            "cmd": "LocationChecks",
            "locations": [location_id],
        }])

        # Remove the physical collection from the game.
        self.game_memory.lock_red_brick_unlock_flag(brick_number)

    # =============================================================
    # Archipelago packets
    # =============================================================

    def on_package(self, cmd, args):
        print(f"PACKET: {cmd}")

        # ---------------------------------------------------------
        # Connected
        # ---------------------------------------------------------

        if cmd == "Connected":
            self.randomized_red_bricks = set(
                args["slot_data"]["randomized_red_bricks"]
            )

            self.nonrandomized_red_bricks = (
                set(range(1, 19))
                - self.randomized_red_bricks
            )

            print(
                f"Randomized red bricks: "
                f"{sorted(self.randomized_red_bricks)}"
            )

            print(
                f"Non-randomized red bricks: "
                f"{sorted(self.nonrandomized_red_bricks)}"
            )

        # ---------------------------------------------------------
        # Received Items
        # ---------------------------------------------------------

        if cmd == "ReceivedItems":
            print(
                f"Received {len(args['items'])} item(s)"
            )

            for item in args["items"]:
                print(f"Item ID: {item.item}")

                # Character receipt needs to send an async
                # LocationChecks packet for the hub-character
                # special case.
                #
                # handle_received_item() itself remains synchronous
                # because on_package() is a synchronous CommonClient
                # callback.
                asyncio.create_task(
                    self.handle_received_item(item)
                )

        super().on_package(cmd, args)

    async def handle_received_item(self, item):
        if self.game_memory is None:
            print(
                "Cannot handle item: "
                "Dolphin is not connected."
            )
            return

        # ---------------------------------------------------------
        # Filler Studs
        # ---------------------------------------------------------

        STUD_VALUES = {
            ITEM_STUDS_10: 10,
            ITEM_STUDS_100: 100,
            ITEM_STUDS_1000: 1000,
            ITEM_STUDS_10000: 10000,
        }

        if item.item in STUD_VALUES:
            amount = STUD_VALUES[item.item]

            self.game_memory.studs += amount

            print(
                f"Received {amount:,} Studs!"
            )

            return

        # ---------------------------------------------------------
        # Gold Brick
        # ---------------------------------------------------------

        if item.item == ITEM_GOLD_BRICK:
            current = self.game_memory.gold_bricks

            if current < 255:
                self.game_memory.gold_bricks = current + 1

                print(
                    f"Received Gold Brick! "
                    f"{current} -> {current + 1}"
                )

            return

        # ---------------------------------------------------------
        # Red Bricks
        # ---------------------------------------------------------

        for name, item_id in RED_BRICK_ITEM_IDS.items():
            if item.item == item_id:
                brick_number = int(name.split()[-1])

                self.archi_red_bricks.add(brick_number)
                self.expected_red_bricks.add(brick_number)

                self.game_memory.unlock_red_brick(
                    brick_number
                )

                print(
                    f"Archipelago gave {name}. "
                    f"Physical brick is now available."
                )

                return

        # ---------------------------------------------------------
        # Characters
        # ---------------------------------------------------------

        for name, item_id in CHARACTER_ITEM_IDS.items():
            if item.item == item_id:
                await self.receive_character(name)
                return

        print(
            f"Unknown LSW3 item ID: {item.item}"
        )


# =================================================================
# Client startup
# =================================================================

def run_client(*launcher_args):
    parser = get_base_parser(
        description=(
            "LEGO Star Wars III: "
            "The Clone Wars Archipelago Client."
        )
    )

    args = parser.parse_args(launcher_args)

    async def _run():
        ctx = LSW3Context(
            args.connect,
            args.password
        )

        ctx.server_task = asyncio.create_task(
            server_loop(ctx),
            name="ServerLoop"
        )

        if gui_enabled:
            ctx.run_gui()

        await ctx.exit_event.wait()
        await ctx.shutdown()

    asyncio.run(_run())


def main():
    run_client()


if __name__ == "__main__":
    main()