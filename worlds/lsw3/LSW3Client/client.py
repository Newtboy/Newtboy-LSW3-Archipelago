# pyrefly: ignore-errors[bad-assignment]
# pyrefly: ignore-errors [missing-attribute]
import sys
import warnings

import worlds.lsw3
import worlds.lsw3.LSW3Client.lsw3_data_pointers

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

# pyrefly: ignore [missing-import]
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
	ITEM_PROGRESSIVE_DOOKU,
	ITEM_PROGRESSIVE_GRIEVOUS,
	ITEM_PROGRESSIVE_VENTRESS
)

from worlds.lsw3.Locations import (
	RED_BRICK_LOCATION_IDS,
	CHARACTER_LOCATION_IDS,
	STUD_LOCATION_IDS,
	SHIP_LOCATION_IDS
)

from .lsw3_data_pointers import CHEAT_CODE_CHARACTERS as chs

from ..character_regions import (
	hub_characters,
	brig_characters,
	minikit_characters,
	ground_battle_characters
)

debug = True

class LSW3Context(CommonContext):
	game = "LEGO Star Wars III: The Clone Wars"
	items_handling = 0b111
	goal_sent = False

	def __init__(self, server_address, password):
		super().__init__(server_address, password)

		self.game_memory: LSW3Memory = None

		self.wallet_level = 1

		self.haveWallets = False

		self.progressiveLevels = False

		self.stud_locations_checked = set()


		self.hub_characters = hub_characters
		self.minikit_characters = minikit_characters
		self.brig_characters = brig_characters
		self.ground_battle_characters = ground_battle_characters

		# NOTE:
		# "Destroyer Droid" is listed as "Droideka" instead
		# "Siover Boll" and "Onaconda Farr" use the spellings from what I saw in game

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

		self.character_state = {}

		self.ship_state = {}

		self.goal_sent = False

	async def check_stud_locations(self):
		studs = self.game_memory.studs

		stud_thresholds = [
			10_000,
			100_000,
			1_000_000,
			10_000_000,
			100_000_000
		]

		for threshold in stud_thresholds:
			if (
					studs >= threshold
					and threshold not in self.stud_locations_checked
			):
				location_name = f"{threshold} Studs"
				location_id = STUD_LOCATION_IDS[location_name]

				await self.send_msgs([{
					"cmd": "LocationChecks",
					"locations": [location_id],
				}])

				self.stud_locations_checked.add(threshold)


	# Gui, what do you want me to say?
	def run_gui(self):
		"""GUI booter"""
		# pyrefly: ignore [missing-import]
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

	# Entre de server
	async def server_auth(self, password_requested=False):
		"""Check with server, connect and setup"""
		await super().server_auth(password_requested)
		import dolphin_memory_engine as dme

		if dme.get_status() == dme.get_status().unHooked:
			ConnectionResetError("Make sure dolphin is running.")

		if self.game_memory is None:
			print("Connecting to Dolphin...")

			try:
				self.game_memory = LSW3Memory()
				print("Connected to Dolphin!")

				self.character_state = {
					character: {
						"ap_received": False,
						"bought": False,
						"location_checked": False,
					}
					for character in self.game_memory.CHARACTERS
				}
				self.ship_state = {
					ship: {
						"ap_received": False,
						"bought": False,
						"location_checked": False,
					}
					for ship in self.game_memory.SHIPS
				}
				self.level_state: dict[str, dict[str, bool]] = {
					level: {
						"ap_received": False,
						"location_checked": False,
					}
					for level in self.game_memory.LEVELS
				}

				asyncio.create_task(self.game_watcher())

			except RuntimeError as e:
				print(f"WARNING: {e}")
			except ConnectionResetError as e:
				print("Reboot dolphin.")

		await self.get_username()
		await self.send_connect()

	# lookit da game
	async def game_watcher(self):
		"""Checks various aspects of the game and ensures running correctly"""
		while True:
			await self.check_connection()
			await self.check_red_bricks()
			await self.check_characters()
			await self.check_ships()
			if self.haveWallets:
				await self.check_studs()
			if (self.progressiveLevels): # {
				await self.check_levels()
			await self.check_stud_locations()
			await self.check_gold_bricks()
			await self.check_cheat_code()

			await asyncio.sleep(0.1)

	async def check_connection(self):
		import dolphin_memory_engine as dme
		if dme.get_status() == dme.get_status().unHooked:
			ConnectionResetError("Make sure dolphin is running.")
			sys.exit()

	async def check_levels(self):
		for level_name in self.game_memory.LEVELS:
			state = self.level_state[level_name]
			is_unlocked = self.game_memory.level_unlocked(level_name)

			# DO NOT let the game unlock it, send the check
			if is_unlocked and not state["ap_received"]:
				self.game_memory.lock_level(level_name)

				location_name = f"Level Completed: {level_name}"
				location_id = worlds.lsw3.LEVEL_LOCATION_IDS[location_name]
				await self.send_msgs([{
					"cmd": "LocationChecks",
					"locations": [location_id],
				}])

			if state["ap_received"]:
				if not is_unlocked:
					self.game_memory.complete_level(level_name)


	async def check_cheat_code(self):
		chars = [
			13,  # N
			26,  # 0
			2,   # C
			20,  # U
			19,  # T
			31,  # 5
		]

		for i in range(len(chs)):
			address = chs[i]
			value = chars[i]

			self.game_memory.write_bytes(address, bytes([value]))


	async def check_studs(self):
		if self.game_memory.studs > self.wallet_cap:
			self.game_memory.studs = self.wallet_cap

	async def check_gold_bricks(self):
		# Gold Bricks can reset when changing zones.
		# Reapply the number actually awarded by AP.
		if self.game_memory.gold_bricks < self.actual_golds:
			self.game_memory.gold_bricks = self.actual_golds

	# Characters
	async def check_characters(self):
		"""go through lsw characters and ensure they're in the right state"""

		for character in self.game_memory.CHARACTERS:
			state = self.character_state[character]

			ap_received = state["ap_received"]
			bought = state["bought"]
			location_checked = state["location_checked"]

			is_unlocked = self.game_memory.character_unlocked(character)

			if is_unlocked and not ap_received:
				state["bought"] = True
				bought = True

			if ap_received:
				if not is_unlocked:
					self.game_memory.unlock_character(character)


			elif bought:
				if not location_checked:
					await self.character_collected(character)
					state["location_checked"] = True

				self.game_memory.lock_character(character)

	async def character_collected(self, character):
		"""
		Report a naturally obtained character as an AP location.
		"""
		location_name = f"Character Unlock: {character}"
		location_id = CHARACTER_LOCATION_IDS[location_name]

		await self.send_msgs([{
			"cmd": "LocationChecks",
			"locations": [location_id],
		}])

	async def check_ships(self):
		"""go through lsw ships and ensure they're in the right state"""

		for ship in self.game_memory.SHIPS:
			state = self.ship_state[ship]

			ap_received = state["ap_received"]
			bought = state["bought"]
			location_checked = state["location_checked"]

			is_unlocked = self.game_memory.ship_unlocked(ship)

			if is_unlocked and not ap_received:
				state["bought"] = True
				bought = True

			if ap_received:
				if not is_unlocked:
					self.game_memory.unlock_ship(ship)

			elif bought:
				if not location_checked:
					await self.ship_collected(ship)
					state["location_checked"] = True

				self.game_memory.lock_ship(ship)

	async def ship_collected(self, ship):
		"""
		Report a naturally obtained ship as an AP location.
		"""
		location_name = f"Ship Unlock: {ship}"
		location_id = SHIP_LOCATION_IDS[location_name]

		await self.send_msgs([{
			"cmd": "LocationChecks",
			"locations": [location_id],
		}])


	async def receive_ship(self, ship):
		"""
		get da ship TM
		"""
		if ship not in self.ship_state:
			print(
				f"WARNING: Received unknown character "
				f"{ship}"
			)
			return

		state = self.ship_state[ship]

		state["ap_received"] = True

		# Give the character immediately.
		self.game_memory.unlock_ship(ship)

		print(
			f"Received character from Archipelago: "
			f"{ship}"
		)

		if (not state["bought"] and not state["location_checked"]):
			print(
				f"{ship} is gonna be a problem.\n"
				f"Checking its associated location."
			)

			await self.ship_collected(ship)

			state["location_checked"] = True


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

		state["ap_received"] = True

		# Give the character immediately.
		self.game_memory.unlock_character(character)

		print(
			f"Received character from Archipelago: "
			f"{character}"
		)

		if (
				(character in self.hub_characters
				 or character in self.minikit_characters
				 or character in self.brig_characters)
				and not state["bought"]
				and not state["location_checked"]
		):
			print(
				f"{character} is a hub character. "
				f"Checking its associated location."
			)

			await self.character_collected(character)

			state["location_checked"] = True

	# Red Brick Stuff
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

		# IT'S JUST A SIMPLE NUMBERS GAME
		if (
				not self.goal_sent
				and all(
			self.game_memory.red_brick_unlocked(brick_number)
			for brick_number in self.randomized_red_bricks
		)
		):

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
			return

		location_name = f"Red Brick Location {brick_number}"
		location_id = RED_BRICK_LOCATION_IDS[location_name]

		await self.send_msgs([{
			"cmd": "LocationChecks",
			"locations": [location_id],
		}])

	# TALK to me, server
	def on_package(self, cmd: str, args: dict[str, dict[str,str]]):
		if debug:
			print(f"PACKET: {cmd}")
			print(f"PACKET DATA: {args!r}")

		import dolphin_memory_engine as dme
		if dme.get_status() == dme.get_status().unHooked or not dme.is_hooked():
			ConnectionResetError("Make sure dolphin is running.")

		if cmd == "Connected":
			self.randomized_red_bricks = set(
				args["slot_data"]["randomized_red_bricks"]
			)

			self.haveWallets = args["slot_data"]["haveWallets"]
			self.progressiveLevels = args["slot_data"]["progressiveLevels"]
			self.nonrandomized_red_bricks = (
					set(range(1, 19))
					- self.randomized_red_bricks
			)

		if cmd == "ReceivedItems":
			if debug:
				print(f"Received {len(args['items'])} item(s)")

			for item in args["items"]:
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

		if item.item == ITEM_PROGRESSIVE_WALLET:
			self.wallet_level += 1

			wallet_caps = [
				10_000,
				100_000,
				1_000_000,
				10_000_000,
				100_000_000,
				999999999999999999999999999999999999999,
			]

			self.wallet_cap = wallet_caps[
				min(self.wallet_level, len(wallet_caps) - 1)
			]
			return
		# }
		progressive_level_prefixes = {
			ITEM_PROGRESSIVE_VENTRESS: "V",
			ITEM_PROGRESSIVE_DOOKU: "D",
			ITEM_PROGRESSIVE_GRIEVOUS: "G",
		}

		prefix = progressive_level_prefixes.get(item.item)

		if prefix is not None:
			for name, level in (worlds.lsw3.LSW3Client.lsw3_data_pointers.LEVELS.items()):
				# Find the next incomplete level in this character's sequence.
				if name.startswith(prefix) and not level.isCompleted():
					state = self.level_state[name]
					self.game_memory.complete_level(name)

					state["ap_received"] = True

					print(f"Progressive level unlocked: {name}")
					break
			else:
				print(
					f"All levels in the {prefix} sequence are completed!"
				)

			return

		# Gold Brick
		if item.item == ITEM_GOLD_BRICK:
			self.actual_golds += 1

			if self.game_memory.gold_bricks < self.actual_golds:
				self.game_memory.gold_bricks = self.actual_golds
			return

		# Red Bricks
		for name, item_id in RED_BRICK_ITEM_IDS.items():

			if item.item == item_id:
				brick_number = int(name.split()[-1])
				state = self.red_brick_state[brick_number]

				state["ap_received"] = True
				state["collected"] = True

				self.game_memory.unlock_red_brick(brick_number)
				return

		for name, item_id in CHARACTER_ITEM_IDS.items():

			if item.item == item_id:

				await self.receive_character(name)

				return

		# Ships
		for name, item_id in worlds.lsw3.SHIP_ITEM_IDS.items():

			if item.item == item_id:
				await self.receive_ship(name)
				return

		print(f"Unknown LSW3 item ID: {item.item}")


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