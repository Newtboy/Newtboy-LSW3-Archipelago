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
)

from worlds.lsw3.Locations import RED_BRICK_LOCATION_IDS


class LSW3Context(CommonContext):
    game = "LEGO Star Wars III: The Clone Wars"
    items_handling = 0b111

    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        
        self.archi_red_bricks = set()

        self.expected_red_bricks = set()

        self.game_memory = None

    async def server_auth(self, password_requested=False):
        await super().server_auth(password_requested)

        if self.game_memory is None:
            print("Connecting to Dolphin...")

            try:
                self.game_memory = LSW3Memory()
                print("Connected to Dolphin!")
                print(f"Gold Bricks: {self.game_memory.gold_bricks}")

                asyncio.create_task(self.game_watcher())

            except RuntimeError as e:
                print(f"WARNING: {e}")

        await self.get_username()
        await self.send_connect()
        
    async def game_watcher(self):
        previous_counts = {
            1: self.game_memory.red_brick_1_8_count,
            2: self.game_memory.red_brick_9_16_count,
            3: self.game_memory.red_brick_17_18_count,
        }

        while True:
            current_counts = {
                1: self.game_memory.red_brick_1_8_count,
                2: self.game_memory.red_brick_9_16_count,
                3: self.game_memory.red_brick_17_18_count,
            }

            # Red Bricks 1-8
            changed = current_counts[1] & ~previous_counts[1]

            for bit in range(8):
                if changed & (1 << bit):
                    self.red_brick_collected(bit + 1)

            # Red Bricks 9-16
            changed = current_counts[2] & ~previous_counts[2]

            for bit in range(8):
                if changed & (1 << bit):
                    self.red_brick_collected(bit + 9)

            # Red Bricks 17-18
            changed = current_counts[3] & ~previous_counts[3]

            for bit in range(2):
                if changed & (1 << bit):
                    self.red_brick_collected(bit + 17)

            previous_counts = current_counts

            await asyncio.sleep(0.1)
            
    def red_brick_collected(self, brick_number):
        name = f"Red Brick {brick_number}"

        print(f"Detected collection of {name}")

        # Only report the location if Archipelago has given us this brick.
        if brick_number not in self.archi_red_bricks:
            print(f"{name} is not currently owned by Archipelago.")
            self.game_memory.lock_red_brick(brick_number)
            return

        print(f"{name} is an Archipelago item. Sending location check.")

        location_id = RED_BRICK_LOCATION_IDS[name]

        self.send_msgs([{
            "cmd": "LocationChecks",
            "locations": [location_id],
        }])

        # Remove the collection flag, but leave the unlock flag alone.
        self.game_memory.clear_red_brick_count(brick_number)
        
    def clear_red_brick_count(self, brick_number):
        if not 1 <= brick_number <= 18:
            raise ValueError("Red brick number must be between 1 and 18")

        if brick_number <= 8:
            address = self.RED_BRICK_1_8_COUNT
            bit = 1 << (brick_number - 1)

        elif brick_number <= 16:
            address = self.RED_BRICK_9_16_COUNT
            bit = 1 << (brick_number - 9)

        else:
            address = self.RED_BRICK_17_18_COUNT
            bit = 1 << (brick_number - 17)

        current = self.read_u8(address)
        self.write_u8(address, current & ~bit)

    def on_package(self, cmd, args):
        print(f"PACKET: {cmd}")

        super().on_package(cmd, args)

        if cmd == "ReceivedItems":
            print(f"Received {len(args['items'])} item(s)")

            for item in args["items"]:
                print(f"Item ID: {item.item}")
                self.handle_received_item(item)

    def handle_received_item(self, item):
        if self.game_memory is None:
            print("Cannot handle item: Dolphin is not connected.")
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

                # Give the physical brick to the player.
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

    ctx.auth = "Whirl"

    asyncio.create_task(ctx.game_watcher())

    await server_loop(ctx)

def main():
    parser = get_base_parser()
    args = parser.parse_args()

    asyncio.run(run_client(args))


if __name__ == "__main__":
    main()