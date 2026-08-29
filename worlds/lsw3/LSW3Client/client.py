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
    ITEM_STUDS_10000,
    ITEM_PROGRESSIVE_WALLET,
)

from worlds.lsw3.Locations import (
    RED_BRICK_LOCATION_IDS,
    CHARACTER_LOCATION_IDS,
    STUD_LOCATION_IDS
)


class LSW3Context(CommonContext):
    game = "LEGO Star Wars III: The Clone Wars"
    items_handling = 0b111
    goal_sent = False

    def __init__(self, server_address, password):
        super().__init__(server_address, password)

        self.game_memory = None
        
        self.wallet_level = 1
        
        self.stud_locations_checked = set()

        # =========================================================
        # Character configuration
        # =========================================================
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
        
        self.minikit_characters = {
            "Admiral Ackbar (Classic)",
            "Captain Antilles (Classic)",
            "Chewbacca (Classic)",
            "Han Solo (Classic)",
            "Lando Calrissian (Classic)",
            "Princess Leia (Classic)",
            "Luke Skywalker (Classic)",
            "Obi-Wan Kenobi (Classic)",
            "Qui-Gon Jinn (Classic)",
            "Rebel Commando (Classic)",
            "Wedge Antilles (Classic)",
            "Boba Fett (Classic)",
            "Greedo (Classic)",
            "Darth Maul (Classic)",
            "Darth Sidious (Classic)",
            "Darth Vader (Classic)",
            "Darth Vader Battle Damaged (Classic)",
            "Vader’s Apprentice (Classic)",
            "Imperial Guard (Classic)",
            "Clone Shadow Trooper (Classic)",
            "Stormtrooper (Classic)",
            "Tusken Raider (Classic)",
        }
        
        self.brig_characters = {
            "Dr Nuvo Vindi",
            "Wat Tambor",
            "Lok Durd",
            "Poggle the Lesser",
            "Nute Gunray",
            "Whorm Loathsom",
        }
        
        self.ground_battle_characters = {
            "Chancellor Palpatine",
            "Grand Moff Tarkin"
        }

        # NOTE:
        # "Destroyer Droid" is listed as "Droideka" instead
        # "Siover Boll" and "Onaconda Farr" use the spellings from what I saw in game
        # =========================================================
        # Red Brick state
        # =========================================================

        self.randomized_red_bricks = set()
        self.nonrandomized_red_bricks = set()

        self.red_brick_state = {
            brick_number: {
                "ap_received": False,
                "collected": False,
                "location_checked": False,
            }
            for brick_number in range(1, 19)
        }
        
        self.actual_golds = 0
        
        self.wallet_level = 0
        self.wallet_cap = 10000

        # =========================================================
        # Character state
        # =========================================================
        #
        self.character_state = {}

        self.goal_sent = False
        
    async def check_stud_locations(self):
        studs = self.game_memory.studs

        stud_thresholds = [
            10000,
            100000,
            1000000,
        ]

        for threshold in stud_thresholds:
            if (
                studs >= threshold
                and threshold not in self.stud_locations_checked
            ):
                location_name = f"{threshold} Studs"
                location_id = STUD_LOCATION_IDS[location_name]

                print(
                    f"Reached {threshold:,} studs! "
                    f"Checking location."
                )

                await self.send_msgs([{
                    "cmd": "LocationChecks",
                    "locations": [location_id],
                }])

                self.stud_locations_checked.add(threshold)

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
            await self.check_studs()
            await self.check_stud_locations()
            await self.check_gold_bricks()

            await asyncio.sleep(0.1)
            
    async def check_studs(self):
        if self.game_memory.studs > self.wallet_cap:
            self.game_memory.studs = self.wallet_cap
            
    async def check_gold_bricks(self):
        # Gold Bricks can reset when changing zones.
        # Reapply the number actually awarded by AP.
        if self.game_memory.gold_bricks < self.actual_golds:
            print(
                f"Restoring Gold Bricks: "
                f"{self.game_memory.gold_bricks} -> "
                f"{self.actual_golds}"
            )
        
            self.game_memory.gold_bricks = self.actual_golds

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
        for brick_number in range(1, 19):
            state = self.red_brick_state[brick_number]

            ap_received = state["ap_received"]
            location_checked = state["location_checked"]
            is_unlocked = self.game_memory.red_brick_unlocked(brick_number)

            if is_unlocked and not ap_received:
                state["collected"] = True

            if (
                state["collected"]
                and not ap_received
                and not location_checked
            ):
                await self.red_brick_collected(brick_number)

                state["location_checked"] = True

                # Remove the physical collection from the game.
                self.game_memory.lock_red_brick_unlock_flag(brick_number)

            if ap_received and not is_unlocked:
                self.game_memory.unlock_red_brick(brick_number)

        # -------------------------------------------------------------
        # Goal
        # -------------------------------------------------------------

        if (
                not self.goal_sent
                and all(
            self.game_memory.red_brick_unlocked(brick_number)
            for brick_number in self.randomized_red_bricks
        )
        ):
            print("All Randomized Red Bricks collected! Game complete.")

            await self.send_msgs([{
                "cmd": "StatusUpdate",
                "status": 30,
            }])

            self.goal_sent = True

    async def red_brick_collected(self, brick_number):
        name = f"Red Brick {brick_number}"

        # This brick is not randomized.
        # Let the base game handle it normally.
        if brick_number not in self.randomized_red_bricks:
            print(
                f"{name} is not randomized. "
                f"Leaving it alone."
            )
            return

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
        
        if item.item == ITEM_PROGRESSIVE_WALLET:
            self.wallet_level += 1

            wallet_caps = [
                10000,       # no wallet
                100000,      # wallet 1
                1000000,     # wallet 2
                10000000,    # wallet 3
                100000000,
            ]

            self.wallet_cap = wallet_caps[
                min(self.wallet_level, len(wallet_caps) - 1)
            ]

            print(
                f"Received Progressive Wallet! "
                f"Wallet level: {self.wallet_level}, "
                f"cap: {self.wallet_cap:,}"
            )

            return
        # ---------------------------------------------------------
        # Gold Brick
        # ---------------------------------------------------------

        if item.item == ITEM_GOLD_BRICK:
            self.actual_golds += 1

            if self.game_memory.gold_bricks < self.actual_golds:
                self.game_memory.gold_bricks = self.actual_golds

            print(
                f"Received Gold Brick! "
                f"AP gold total: {self.actual_golds}"
            )

            return

        # ---------------------------------------------------------
        # Red Bricks
        # ---------------------------------------------------------

        for name, item_id in RED_BRICK_ITEM_IDS.items():
            if item.item == item_id:
                brick_number = int(name.split()[-1])

                state = self.red_brick_state[brick_number]

                state["ap_received"] = True
                state["collected"] = True

                self.game_memory.unlock_red_brick(brick_number)

                print(f"Archipelago gave {name}.")
                
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