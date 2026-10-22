# pyrefly: ignore-errors [unknown-name]
import sys

# pyrefly: ignore [missing-import]
from BaseClasses import Region, ItemClassification
from rule_builder.rules import HasAllCounts
# pyrefly: ignore [missing-import]
from worlds.AutoWorld import World

import worlds.lsw3.Items
import worlds.lsw3.character_regions
from .LSW3Option import LSW3Options

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
	SHIP_ITEM_IDS,
	ITEM_PROGRESSIVE_DOOKU,
	ITEM_PROGRESSIVE_GRIEVOUS,
	ITEM_PROGRESSIVE_VENTRESS
)

from .Locations import (
	LSW3Location,
	RED_BRICK_LOCATION_IDS,
	CHARACTER_LOCATION_IDS,
	STUD_LOCATION_IDS,
	SHIP_LOCATION_IDS,
	LEVEL_COMPLETION_LOCATION_IDS
)

from .character_regions import (
	minikit_characters,
	brig_characters,
	ground_battle_characters,
)

from .ship_regions import (
	separatist_ships,
	republic_ships
)

from .character_regions import (
    jedi,
    sith,
    grappling_hook,
    protocol,
    astromech,
    hover,
    high_jump,
    short,
    commander,
    clone,
    bounty_hunter,
    silver_destroyer,
    gold_destroyer,
    target,
    electric_panels,
    sniper,
    tx_20_panels,
)

########################################## Launcher Code ###################################################

# pyrefly: ignore [missing-import]
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
	# pyrefly: ignore [bad-argument-type]
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


# pyrefly: ignore [missing-source-for-stubs]
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
	# pyrefly: ignore [unknown-name]
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
    from worlds.lsw3.startup import main
    main()


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

class LSW3World(World):
	game = GAME_NAME

	options_dataclass = LSW3Options
	# pyrefly: ignore[bad-override-mutable-attribute]
	options: LSW3Options

	numProgWallets = 5

	from .Items import JUNK_ITEM_IDS

	item_name_to_id = {
		"Gold Brick": ITEM_GOLD_BRICK,

		**RED_BRICK_ITEM_IDS,
		**CHARACTER_ITEM_IDS,
		**SHIP_ITEM_IDS,

		"10 Studs": ITEM_STUDS_10,
		"100 Studs": ITEM_STUDS_100,
		"1000 Studs": ITEM_STUDS_1000,
		"10000 Studs": ITEM_STUDS_10000,

		**JUNK_ITEM_IDS,

		"Progressive Wallet": ITEM_PROGRESSIVE_WALLET,
		"Progressive Ventress": ITEM_PROGRESSIVE_VENTRESS,
		"Progressive Grievous": ITEM_PROGRESSIVE_GRIEVOUS,
		"Progressive Dooku": ITEM_PROGRESSIVE_DOOKU,

	}

	item_name_to_classification = {
		"Gold Brick": ItemClassification.useful,

		"10 Studs": ItemClassification.filler,
		"100 Studs": ItemClassification.filler,
		"1000 Studs": ItemClassification.filler,
		"10000 Studs": ItemClassification.filler,

		**{
			name: ItemClassification.filler
			for name in JUNK_ITEM_IDS
		},

		"Progressive Ventress": ItemClassification.progression,
		"Progressive Grievous": ItemClassification.progression,
		"Progressive Dooku": ItemClassification.progression,

		**{
			name: ItemClassification.progression
			for name in RED_BRICK_ITEM_IDS
		},

		**{
			name: ItemClassification.progression
			for name in CHARACTER_ITEM_IDS
		},

		**{
			name: ItemClassification.progression
			for name in SHIP_ITEM_IDS
		},

		"Progressive Wallet": ItemClassification.progression,
	}

	location_name_to_id = {
		**RED_BRICK_LOCATION_IDS,
		**CHARACTER_LOCATION_IDS,
		**STUD_LOCATION_IDS,
		**SHIP_LOCATION_IDS,
		**LEVEL_COMPLETION_LOCATION_IDS,
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

		# Level completion locations
		for name, location_id in LEVEL_COMPLETION_LOCATION_IDS.items():
			menu.locations.append(
				LSW3Location(
					self.player,
					name,
					location_id,
					menu,
				)
			)


		used_characters = self.get_used_characters()

		for location_name, location_id in CHARACTER_LOCATION_IDS.items():
			character_name = location_name.removeprefix("Character Unlock: ")

			if character_name in used_characters:
				menu.locations.append(
					LSW3Location(
						self.player,
						location_name,
						location_id,
						menu,
					)
				)

		if (self.options.randomize_ships.value): # {
			for name, location_id in SHIP_LOCATION_IDS.items():
				menu.locations.append(
					LSW3Location(
						self.player,
						name,
						location_id,
						menu,
					)
				)
			# }
		# }
	# }


	def create_items(self):
		red_brick_count = self.options.red_brick_count.value

		# Red Bricks
		self.randomized_red_bricks = self.random.sample(
			list(RED_BRICK_ITEM_IDS.keys()),
			red_brick_count,
		)

		# Characters eligible for randomization.
		eligible_characters = self.get_used_characters()

		# Each category must contribute at least one character.
		character_categories = [
			jedi,
			sith,
			grappling_hook,
			protocol,
			astromech,
			hover,
			high_jump,
			short,
			commander,
			clone,
			bounty_hunter,
			silver_destroyer,
			gold_destroyer,
			target,
			electric_panels,
			sniper,
			tx_20_panels,
		]

		# Choose one available character from each category, guaranteeing you can get at least 1 of every kind
		guaranteed_characters = set()

		for category in character_categories:
			available = list(category & eligible_characters)

			if available:
				guaranteed_characters.add(self.random.choice(available))

		# Calculate the configured character count.
		character_count = round(
			len(eligible_characters)
			* self.options.character_percent.value
			/ 100
		)

		# Ensure every guaranteed character fits in the pool.
		character_count = max(character_count, len(guaranteed_characters))

		# Fill the remaining slots randomly without duplicates.
		remaining_characters = list(
			eligible_characters - guaranteed_characters
		)

		self.randomized_characters = list(guaranteed_characters)
		self.randomized_characters.extend(
			self.random.sample(
				remaining_characters,
				character_count - len(guaranteed_characters),
			)
		)

		# Progressive Wallets
		if self.options.progressive_wallets.value:
			for _ in range(self.numProgWallets):
				self.multiworld.itempool.append(
					self.create_item("Progressive Wallet")
				)

		# Randomized Red Bricks
		for name in self.randomized_red_bricks:
			self.multiworld.itempool.append(
				self.create_item(name)
			)

		# Randomized Characters
		for name in self.randomized_characters:
			self.multiworld.itempool.append(
				self.create_item(name)
			)

		# Randomized Ships
		if (self.options.randomize_ships.value): # {
			for ship in SHIP_ITEM_IDS:
				self.multiworld.itempool.append(
					self.create_item(ship)
				)

		level_counts = {"D": 0, "V": 0, "G": 0}
		unmatched_levels = []

		for location_name in LEVEL_COMPLETION_LOCATION_IDS:
			level_name = location_name.removeprefix("Level Completed: ")

			if len(level_name) >= 2 and level_name[0] in level_counts and level_name[1].isdigit():
				level_counts[level_name[0]] += 1
			else:
				unmatched_levels.append(level_name)
		# Progressive Levels
		if self.options.progressive_levels.value:
			for _ in range(level_counts["D"]):
				self.multiworld.itempool.append(
					self.create_item("Progressive Dooku")
				)

			for _ in range(level_counts["V"]):
				self.multiworld.itempool.append(
					self.create_item("Progressive Ventress")
				)

			for _ in range(level_counts["G"]):
				self.multiworld.itempool.append(
					self.create_item("Progressive Grievous")
				)

		# Filler
		filler_items = [
			"10 Studs",
			"100 Studs",
			"1000 Studs",
			"10000 Studs",
			"Asthmatic Robot",
			"Roger Roger",
			"Jedi Scum!"
		]

		# Calculate the number of locations and items for this player.
		location_count = sum(
			1
			for location in self.multiworld.get_locations()
			if location.player == self.player
		)

		item_count = sum(
			1
			for item in self.multiworld.itempool
			if item.player == self.player
		)

		# Fill every remaining location with a filler item.
		remaining = location_count - item_count

		if remaining < 0:
			raise Exception(
				f"LSW3 has {-remaining} too many items! "
				f"Items: {item_count}, Locations: {location_count}"
			)

		for _ in range(remaining):
			self.multiworld.itempool.append(
				self.create_item(self.random.choice(filler_items))
			)

	def get_used_characters(self):
		used_characters = set()

		used_characters.update(worlds.lsw3.character_regions.hub_characters)
		used_characters.update(worlds.lsw3.character_regions.level_unlock_characters)

		if self.options.use_brig_characters.value:
			used_characters.update(brig_characters)

		if self.options.use_groundBattle_characters.value:
			used_characters.update(ground_battle_characters)

		if self.options.use_minikit_characters.value:
			used_characters.update(minikit_characters)

		return used_characters

	def create_item(self, name):
		return LSW3Item(
			name,
			self.item_name_to_classification[name],
			self.item_name_to_id[name],
			self.player,
		)

	def set_rules(self):
		from .Rules import set_rules

		if self.options.progressive_levels.value:
			self.multiworld.completion_condition[self.player] = (
				lambda state: state.has("Progressive Ventress", self.player, 6)
							  and state.has("Progressive Grievous", self.player, 6)
							  and state.has("Progressive Dooku", self.player, 6)
			)
		else:
			self.multiworld.completion_condition[self.player] = (
				lambda state: all(
					state.has(item, self.player)
					for item in self.randomized_red_bricks
				)
			)
		set_rules(self)

	def generate_basic(self):
		pass

	def fill_slot_data(self):
		return {
			"randomized_red_bricks": [
				int(name.split()[-1])
				for name in self.randomized_red_bricks
			],
			"randomizedShips": self.options.randomize_ships.value,
			"haveWallets": self.options.progressive_wallets.value,
			"progressiveLevels": self.options.progressive_levels.value,
		}

