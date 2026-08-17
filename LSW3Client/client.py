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


class LSW3Context(CommonContext):
    game = "LEGO Star Wars III: The Clone Wars"
    items_handling = 0b111

    def __init__(self, server_address, password):
        super().__init__(server_address, password)

        self.game_memory = None

    async def server_auth(self, password_requested=False):
        await super().server_auth(password_requested)

        if self.game_memory is None:
            print("Connecting to Dolphin...")

            try:
                self.game_memory = LSW3Memory()
                print("Connected to Dolphin!")
                print(f"Gold Bricks: {self.game_memory.gold_bricks}")

            except RuntimeError as e:
                print(f"WARNING: {e}")

        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd, args):
        print(f"PACKET: {cmd}")

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

                unlocked = self.game_memory.unlock_red_brick(
                    brick_number
                )

                if unlocked:
                    print(f"Unlocked {name}")
                else:
                    print(f"{name} was already unlocked.")

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


async def run_client(args):
    ctx = LSW3Context(args.connect, args.password)

    ctx.auth = "Whirl"

    await server_loop(ctx)


def main():
    parser = get_base_parser()
    args = parser.parse_args()

    asyncio.run(run_client(args))


if __name__ == "__main__":
    main()