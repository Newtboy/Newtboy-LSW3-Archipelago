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

from CommonClient import CommonContext, get_base_parser, server_loop
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

from worlds.lsw3.Locations import RED_BRICK_LOCATION_IDS


class LSW3Context(CommonContext):
    game = "LEGO Star Wars III: The Clone Wars"
    items_handling = 0b111
    goal_sent = False

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        
        self.archi_red_bricks = set()

        self.expected_red_bricks = set()
        
        self.nonrandomized_red_bricks = set()

        self.game_memory = None

    async def server_auth(self, password_requested=False):
        await super().server_auth(password_requested)

        if self.game_memory is None:
            print("Connecting to Dolphin...")

            try:
                self.game_memory = LSW3Memory()
                print("Connected to Dolphin!")

                asyncio.create_task(self.game_watcher())

            except RuntimeError as e:
                print(f"WARNING: {e}")

        await self.get_username()
        await self.send_connect()
        
    async def game_watcher(self):
        previous_1_8 = self.game_memory.red_bricks_1_8
        previous_9_16 = self.game_memory.red_bricks_9_16
        previous_17_18 = self.game_memory.red_bricks_17_18

        while True:
            current_1_8 = self.game_memory.red_bricks_1_8
            current_9_16 = self.game_memory.red_bricks_9_16
            current_17_18 = self.game_memory.red_bricks_17_18

            # Red Bricks 1-8
            for brick_number in range(1, 9):
                was_unlocked = previous_1_8 & (1 << (brick_number - 1))
                is_unlocked = current_1_8 & (1 << (brick_number - 1))

                if not was_unlocked and is_unlocked:
                    await self.red_brick_collected(brick_number)

            # Red Bricks 9-16
            for brick_number in range(9, 17):
                bit = 1 << (brick_number - 9)

                was_unlocked = previous_9_16 & bit
                is_unlocked = current_9_16 & bit

                if not was_unlocked and is_unlocked:
                    await self.red_brick_collected(brick_number)

            # Red Bricks 17-18
            for brick_number in range(17, 19):
                bit = 1 << (brick_number - 17)

                was_unlocked = previous_17_18 & bit
                is_unlocked = current_17_18 & bit

                if not was_unlocked and is_unlocked:
                    await self.red_brick_collected(brick_number)

            previous_1_8 = current_1_8
            previous_9_16 = current_9_16
            previous_17_18 = current_17_18
            
            if not self.goal_sent and self.game_memory.all_red_bricks_unlocked():
                print("All 18 Red Bricks collected! Game complete.")

                await self.send_msgs([{
                    "cmd": "StatusUpdate",
                    "status": 30,  # CLIENT_GOAL
                }])

                self.goal_sent = True

            await asyncio.sleep(0.1)
            
    async def red_brick_collected(self, brick_number):
        name = f"Red Brick {brick_number}"

        # Archipelago caused this brick to appear.
        if brick_number in self.expected_red_bricks:
            print(
                f"{name} appeared because Archipelago gave it to us."
            )

            self.expected_red_bricks.remove(brick_number)

            # Don't let the game count the AP-granted brick
            # as a physical collection.
            self.game_memory.lock_red_brick_count(brick_number)

            return

        # Player physically collected it.
        print(f"Detected physical collection of {name}")

        # This brick is not randomized.
        # Let the base game handle it normally.
        if brick_number not in self.randomized_red_bricks:
            print(f"{name} is not randomized. Leaving it alone.")
            return

        # This brick is randomized, so the collection is an AP location check.
        print(
            f"{name} is randomized. "
            f"Sending location check."
        )

        location_id = RED_BRICK_LOCATION_IDS[name]

        await self.send_msgs([{
            "cmd": "LocationChecks",
            "locations": [location_id],
        }])

        # Remove the physical collection from the game.
        self.game_memory.lock_red_brick_unlock_flag(brick_number)

    def on_package(self, cmd, args):
        print(f"PACKET: {cmd}")

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

        if cmd == "ReceivedItems":
            print(f"Received {len(args['items'])} item(s)")

            for item in args["items"]:
                print(f"Item ID: {item.item}")
                self.handle_received_item(item)

        super().on_package(cmd, args)
        
    def handle_received_item(self, item):
        if self.game_memory is None:
            print("Cannot handle item: Dolphin is not connected.")
            return
        
        # Filler Studs
        STUD_VALUES = {
            ITEM_STUDS_10: 10,
            ITEM_STUDS_100: 100,
            ITEM_STUDS_1000: 1000,
            ITEM_STUDS_10000: 10000,
        }
        if item.item in STUD_VALUES:
            amount = STUD_VALUES[item.item]
            self.game_memory.studs += amount
            print(f"Received {amount:,} Studs!")
            return

        # Gold Brick
        if item.item == ITEM_GOLD_BRICK:
            current = self.game_memory.gold_bricks

            if current < 255:
                self.game_memory.gold_bricks = current + 1

                print(
                    f"Received Gold Brick! "
                    f"{current} -> {current + 1}"
                )

            return

        # Red Bricks
        for name, item_id in RED_BRICK_ITEM_IDS.items():
            if item.item == item_id:
                brick_number = int(name.split()[-1])

                self.archi_red_bricks.add(brick_number)
                self.expected_red_bricks.add(brick_number)

                self.game_memory.unlock_red_brick(brick_number)

                print(
                    f"Archipelago gave {name}. "
                    f"Physical brick is now available."
                )

                return

        # Characters
        for name, item_id in CHARACTER_ITEM_IDS.items():
            if item.item == item_id:
                print(f"Received character: {name}")

                if not self.game_memory.character_unlocked(name):
                    self.game_memory.unlock_character(name)
                    print(f"Unlocked {name}")
                else:
                    print(f"{name} was already unlocked.")

                return

        print(f"Unknown LSW3 item ID: {item.item}")
    
    def send_location_check(self, location_id):
        for name, item_id in RED_BRICK_ITEM_IDS.items():
            if location_id == item_id:
                num = int(name.split()[-1])

                if self.game_memory.lock_red_brick(num):
                    print(f"Locked {name}")
                else:
                    print(f"{name} was already locked.")

                break

        self.send_msgs([{
            "cmd": "LocationChecks",
            "locations": [location_id],
        }])


async def run_client(args):
    ctx = LSW3Context(args.connect, args.password)

    ctx.auth = args.username

    await server_loop(ctx)

def main():
    parser = get_base_parser()
    args = parser.parse_args()

    asyncio.run(run_client(args))


if __name__ == "__main__":
    main()