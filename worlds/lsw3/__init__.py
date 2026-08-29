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
    ITEM_STUDS_10000,
    ITEM_PROGRESSIVE_WALLET,
)

from .Locations import (
    LSW3Location,
    RED_BRICK_LOCATION_IDS,
    CHARACTER_LOCATION_IDS,
    STUD_LOCATION_IDS,
)

from .LSW3Client.client import (
    minikit_characters,
    brig_characters,
    ground_battle_characters,
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
        "10000 Studs": ITEM_STUDS_10000,

        "Progressive Wallet": ITEM_PROGRESSIVE_WALLET,
    }

    item_name_to_classification = {
        "Gold Brick": ItemClassification.useful,

        "10 Studs": ItemClassification.filler,
        "100 Studs": ItemClassification.filler,
        "1000 Studs": ItemClassification.filler,
        "10000 Studs": ItemClassification.filler,

        **{
            name: ItemClassification.progression
            for name in RED_BRICK_ITEM_IDS
        },

        **{
            name: ItemClassification.progression
            for name in CHARACTER_ITEM_IDS
        },
        
        "Progressive Wallet": ItemClassification.progression,
    }

    location_name_to_id = {
        **RED_BRICK_LOCATION_IDS,
        **CHARACTER_LOCATION_IDS,
        **STUD_LOCATION_IDS,
    }

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
            
        for name, location_id in STUD_LOCATION_IDS.items():
            menu.locations.append(
                LSW3Location(
                    self.player,
                    name,
                    location_id,
                    menu,
                )
            )
            
        # Character locations.
        for name, location_id in CHARACTER_LOCATION_IDS.items():
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

        # =========================================================
        # Red Bricks
        # =========================================================

        self.randomized_red_bricks = self.random.sample(
            list(RED_BRICK_ITEM_IDS.keys()),
            red_brick_count,
        )

        # =========================================================
        # Characters
        # =========================================================

        # Characters forced into the randomized pool by toggles.
        forced_characters = set()

        if self.options.use_minikit_characters.value:
            forced_characters.update(MINIKIT_CHARACTERS)

        if self.options.use_groundBattle_characters.value:
            forced_characters.update(GROUND_BATTLE_CHARACTERS)

        if self.options.use_brig_characters.value:
            forced_characters.update(BRIG_CHARACTERS)

        # The percentage only applies to characters that aren't
        # already being forced into the randomized pool.
        randomizable_characters = (
                set(CHARACTER_ITEM_IDS.keys()) - forced_characters
        )

        character_count = round(
            len(randomizable_characters)
            * self.options.character_percent.value
            / 100
        )

        self.randomized_characters = self.random.sample(
            list(randomizable_characters),
            character_count,
        )

        # Add the forced characters.
        self.randomized_characters.extend(forced_characters)

        # This is the ACTUAL number of randomized character locations.
        randomized_character_count = len(self.randomized_characters)

        # =========================================================
        # Progressive Wallets
        # =========================================================

        if self.options.progressive_wallets.value:
            for _ in range(3):
                self.multiworld.itempool.append(
                    self.create_item("Progressive Wallet")
                )

        # =========================================================
        # Randomized Red Bricks
        # =========================================================

        for name in self.randomized_red_bricks:
            self.multiworld.itempool.append(
                self.create_item(name)
            )

        # =========================================================
        # Randomized Characters
        # =========================================================

        for name in self.randomized_characters:
            self.multiworld.itempool.append(
                self.create_item(name)
            )

        # =========================================================
        # Filler
        # =========================================================

        filler_items = [
            "10 Studs",
            "100 Studs",
            "1000 Studs",
            "10000 Studs",
        ]

        # Non-randomized red brick locations.
        remaining = (
                len(RED_BRICK_LOCATION_IDS)
                - red_brick_count
        )

        # Non-randomized character locations.
        remaining += (
                len(CHARACTER_LOCATION_IDS)
                - randomized_character_count
        )

        # Three wallet locations/items if wallets aren't enabled.
        if not self.options.progressive_wallets.value:
            remaining += 3

        for _ in range(remaining):
            self.multiworld.itempool.append(
                self.create_item(
                    self.random.choice(filler_items)
                )
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
            for name in self.randomized_red_bricks
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
        
########################################## Launcher Code ###################################################

from worlds.LauncherComponents import Component, components, Type, launch

import json
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
import asyncio

CONFIG_DIR = Path.home() / "AppData" / "Roaming" / "Archipelago" / "LSW3"
CONFIG_FILE = CONFIG_DIR / "config.json"

def run_client_launcher(*args: str):
    asyncio.run(run_client(*args))

def show_message(title: str, message: str):
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        title,
        message,
        parent=root,
    )

    root.destroy()


def ask_dolphin_path():
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Select Dolphin Emulator",
        filetypes=[
            ("Dolphin Emulator", "Dolphin.exe"),
            ("Executable files", "*.exe"),
            ("All files", "*.*"),
        ],
        parent=root,
    )

    root.destroy()

    return path


def get_dolphin_path():
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                config = json.load(f)

            path = Path(config.get("dolphin_path", ""))

            if path.is_file():
                return path

        except (OSError, json.JSONDecodeError):
            pass

    path = ask_dolphin_path()

    if not path:
        return None

    path = Path(path)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "dolphin_path": str(path),
            },
            f,
            indent=4,
        )

    return path


def show_step(message: str):
    show_message(
        "LEGO Star Wars III: The Clone Wars",
        message,
    )

import psutil

def dolphin_is_running():
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] and process.info["name"].lower() == "dolphin.exe":
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return False

def run_client(*launcher_args):
    parser = get_base_parser(
        description="LEGO Star Wars III: The Clone Wars Archipelago Client."
    )

    args = parser.parse_args(launcher_args)

    async def _run():
        ctx = LSW3Context(args.connect, args.password)

        if gui_enabled:
            ctx.run_gui()

        await server_loop(ctx, args)

    asyncio.run(_run())


def main():
    run_client()


if __name__ == "__main__":
    main()

def launch_client(*args):
    dolphin_path = get_dolphin_path()

    if dolphin_path is None:
        return

    print(f"Launching Dolphin: {dolphin_path}")

    if not dolphin_is_running():
        subprocess.Popen([str(dolphin_path)])

    show_step(
        "Open LEGO Star Wars III."
    )

    show_step(
        "Load/Create a save file.\n\n"
        "Do not start the game."
    )

    show_step(
        "Launching client."
    )

    from .LSW3Client.client import run_client

    launch(
        run_client,
        name="LEGO Star Wars III: The Clone Wars Client",
    )
    
components.append(
    Component(
        display_name="LEGO Star Wars III: The Clone Wars",
        func=launch_client,
        component_type=Type.CLIENT,
        game_name="LEGO Star Wars III: The Clone Wars",
        description="Archipelago client for LEGO Star Wars III: The Clone Wars.",
    )
)

########################################## Launcher World End ################################################