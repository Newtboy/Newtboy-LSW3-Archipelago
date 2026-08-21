from BaseClasses import Region, ItemClassification
from worlds.AutoWorld import World

from .options import LSW3Options

from .Items import (
    LSW3Item,
    GAME_NAME,
    ITEM_GOLD_BRICK,
    RED_BRICK_ITEM_IDS,
    CHARACTER_ITEM_IDS,
    ITEM_STUDS_10,
    ITEM_STUDS_100,
    ITEM_STUDS_1000,
    ITEM_STUDS_10000
)

from .Locations import (
    LSW3Location,
    RED_BRICK_LOCATION_IDS,
)

from ...worlds.LauncherComponents import Component, components, Type

import time
import tkinter as tk
from tkinter import messagebox


def show_error(message: str):
    root = tk.Tk()
    root.withdraw()

    messagebox.showerror(
        "LEGO Star Wars III: The Clone Wars",
        message,
    )

    root.destroy()


def launch_lsw3_client(*args: str):
    # TODO: Launch Dolphin
    print("Launching Dolphin...")

    # TODO: Find LEGO Star Wars III in Dolphin's library
    print("Finding LEGO Star Wars III...")

    # TODO: Launch LEGO Star Wars III
    print("Launching LEGO Star Wars III...")

    # TODO: Send:
    # Plus
    # A
    # A
    # A

    time.sleep(5)

    # Start the actual Archipelago client as a subprocess.
    from .client import run_client

    from worlds.LauncherComponents import launch

    launch(
        run_client,
        name="LEGO Star Wars III: The Clone Wars Client",
        args=args,
    )


components.append(
    Component(
        display_name="LEGO Star Wars III: The Clone Wars",
        func=launch_lsw3_client,
        component_type=Type.CLIENT,
        game_name="LEGO Star Wars III: The Clone Wars",
        description="Archipelago client for LEGO Star Wars III: The Clone Wars.",
    )
)


class LSW3World(World):
    game = GAME_NAME
    
    options_dataclass = LSW3Options
    options: LSW3Options

    item_name_to_id = {
        "Gold Brick": ITEM_GOLD_BRICK,
        **RED_BRICK_ITEM_IDS,
        **CHARACTER_ITEM_IDS,
        "10 Studs": ITEM_STUDS_10,
        "100 Studs": ITEM_STUDS_100,
        "1000 Studs": ITEM_STUDS_1000,
        "10000 Studs": ITEM_STUDS_10000
    }

    item_name_to_classification = {
        "Gold Brick": ItemClassification.useful,

        "10 Studs": ItemClassification.filler,
        "100 Studs": ItemClassification.filler,
        "1000 Studs": ItemClassification.filler,
        "10000 Studs": ItemClassification.filler,

        **{
            name: ItemClassification.useful
            for name in RED_BRICK_ITEM_IDS
        },

        **{
            name: ItemClassification.useful
            for name in CHARACTER_ITEM_IDS
        },
    }

    location_name_to_id = RED_BRICK_LOCATION_IDS

    def create_regions(self):
        menu = Region(
            "Menu",
            self.player,
            self.multiworld,
        )

        self.multiworld.regions.append(menu)

        for name, location_id in RED_BRICK_LOCATION_IDS.items():
            menu.locations.append(
                LSW3Location(
                    self.player,
                    name,
                    location_id,
                    menu,
                )
            )

    def create_items(self):
        red_brick_count = self.options.red_brick_count.value

        self.randomized_red_bricks = self.random.sample(
            list(RED_BRICK_ITEM_IDS.keys()),
            red_brick_count,
        )

        # Add randomized Red Bricks.
        for name in self.randomized_red_bricks:
            self.multiworld.itempool.append(
                self.create_item(name)
            )

        # Fill remaining locations with filler.
        filler_items = [
            "10 Studs",
            "100 Studs",
            "1000 Studs",
            "10000 Studs",
        ]

        remaining = len(RED_BRICK_LOCATION_IDS) - red_brick_count

        for _ in range(remaining):
            name = self.random.choice(filler_items)

            self.multiworld.itempool.append(
                self.create_item(name)
            )
            
    def create_item(self, name):
        return LSW3Item(
            name,
            self.item_name_to_classification[name],
            self.item_name_to_id[name],
            self.player,
        )

    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: all(
            state.has(name, self.player)
            for name in RED_BRICK_ITEM_IDS
        )
        
    def generate_basic(self):
        pass
    
    def fill_slot_data(self):
        return {
            "randomized_red_bricks": [
                int(name.split()[-1])
                for name in self.randomized_red_bricks
            ],
        }