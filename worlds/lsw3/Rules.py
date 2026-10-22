from BaseClasses import ItemClassification
from rule_builder.rules import Has, HasAllCounts, True_, Rule, CanReachLocation
import worlds.lsw3
from rule_builder.rules import Has, HasFromListUnique
from . import LSW3Location, Regions
from .Locations import LEVEL_COMPLETION_LOCATION_IDS
from .ship_regions import republic_ships
from .character_regions import *


def set_rules(world: worlds.lsw3.LSW3World):
	player = world.player
	l = world.get_used_characters()

	character_level_dict: dict[str, list] = {
		"GA": [
			"Anakin Skywalker",
			"Padme Amidala",
			"Obi-Wan Kenobi",
		],
		# Count Dooku
		"D1":  # Battle of Geonosis
			[
				"Mace Windu",
				"Kit Fisto",
				"Ki-Adi-Mundi",
			],
		"D2":  # Gungan General
			[
				"Jar Jar Binks",
				"Commander Stone",
				"Clone Trooper",
			],
		"D3":  # Jedi Crash
			[
				"Ahsoka",
				"Aayla Secura",
				"Commander Bly",
			],
		"D4":  # Defenders of Peace
			[
				"Wag Too",
			],
		"D5":  # Weapons Factory
			[
				"Luminara Unduli",
				"Barriss Offee",
				"Captain Rex",
			],
		"D6":  # Legacy of Terror
			[
				"Commander Cody",
			],
		# General Grievous
		"G1":  # Duel of the Droids
			[
				"R3-S6",
				"R2-D2",
			],
		"G2":  # Shadow of Malevolence
			[
				"Plo Koon",
			],
		"G3":  # Destroy Malevolence
			[
				"C-3PO",
			],
		"G4":  # Lair of Grievous
			[
				"Nahdar Vebb",
				"Commander Fil",
				"Heavy Weapons Clone Trooper",
			],
		"G5":  # Rookies
			[
				"Hevy",
				"Echo",
				"Fives",
			],
		"G6":  # Grievous Intrigue
			[
				"Adi Gallia",
				"Eeth Koth",
			],
		# Asajj Ventress
		"V1":  # The Hidden Enemy
			[],
		"V2":  # Ambush
			[
				"Yoda",
				"Lieutenant Thire",
				"Jek",
				"Rys",
			],
		"V3":  # Blue Shadow Virus
			[],
		"V4":  # Storm Over Ryloth
			[],
		"V5":  # Innocents of Ryloth
			[
				"Waxer",
				"Boil",
			],
		"V6":  # Liberty on Ryloth
			[
				"Commander Ponds",
			]
	}

	used_characters = world.get_used_characters()

	# Only characters that can appear in this world
	available_jedi = jedi & used_characters
	available_sith = sith & used_characters
	available_grapplers = grappling_hook & used_characters
	available_protocol = protocol & used_characters
	av_astromech = astromech & used_characters
	av_high_jump = high_jump & used_characters # it's just jar jar but it's here for consistency
	av_hover = hover & used_characters
	av_short = short & used_characters
	av_commander = commander & used_characters
	av_clone = clone & used_characters
	av_bounty_hunter = bounty_hunter & used_characters
	av_silver_br = silver_destroyer & used_characters
	av_gold_br = gold_destroyer & used_characters
	av_target = target & used_characters
	av_electric = electric_panels & used_characters
	av_sniper = sniper & used_characters
	av_tx20 = tx_20_panels & used_characters

	# Ability requirements
	has_force = HasFromListUnique(*available_jedi, count=1)
	has_dark_force = HasFromListUnique(*available_sith, count=1) | (Has("Red Brick 2") & HasFromListUnique(*available_jedi, count=1))
	has_grappler = HasFromListUnique(*available_grapplers, count=1)
	has_protocol = HasFromListUnique(*available_protocol, count=1)
	has_astromech = HasFromListUnique(*av_astromech, count=1)
	has_high_jump = HasFromListUnique(*av_high_jump, count=1)
	has_hover = HasFromListUnique(*av_hover, count=1)
	has_short = HasFromListUnique(*av_short, count=1)
	has_commander = HasFromListUnique(*av_commander, count=1)
	has_clone = HasFromListUnique(*av_clone, count=1)
	has_bounty_hunter = HasFromListUnique(*av_bounty_hunter, count=1)
	has_silver_br = HasFromListUnique(*av_silver_br, count=1)
	has_gold_br = HasFromListUnique(*av_gold_br, count=1)
	has_target = HasFromListUnique(*av_target, count=1)
	has_electric = HasFromListUnique(*av_electric, count=1)
	has_sniper = HasFromListUnique(*av_sniper, count=1)
	has_tx20 = HasFromListUnique(*av_tx20, count=1)

	has_republic_ship = HasFromListUnique(*republic_ships, count=1)
	has_separatist_ship = HasFromListUnique(*worlds.lsw3.separatist_ships, count=1)

	using_wallets = world.options.progressive_wallets.value
	using_ships = world.options.randomize_ships.value

	#  Helper functions
	def set_brick_rule(number: int, rule: Rule = True_()):
		location = world.multiworld.get_location(
			f"Red Brick Location {number}", player
		)
		location.access_rule = rule.resolve(world)

	def has_character_with(*attributes):
		available = used_characters.copy()

		for attribute in attributes:
			available &= attribute

		return HasFromListUnique(*available, count=1)

	# Red bricks
	set_brick_rule(1, has_silver_br & (HasAllCounts({"Progressive Wallet": 1}) if using_wallets else True_()))
	set_brick_rule(2, has_dark_force & (has_republic_ship if using_ships else True_()))
	set_brick_rule(3, (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(4, (has_republic_ship if using_ships else True_()) & has_grappler & has_clone & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(5, has_high_jump & has_silver_br & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(6, has_high_jump & has_silver_br & (HasAllCounts({"Progressive Wallet": 4}) if using_wallets else True_()))
	set_brick_rule(7, has_grappler & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(8, has_force & (HasAllCounts({"Progressive Wallet": 3}) if using_wallets else True_()))
	set_brick_rule(9, has_force & has_grappler & (HasAllCounts({"Progressive Wallet": 3}) if using_wallets else True_()))
	set_brick_rule(10, has_silver_br & (HasAllCounts({"Progressive Wallet": 4}) if using_wallets else True_()) & (has_republic_ship if using_ships else True_()))
	set_brick_rule(11, has_dark_force & (has_character_with(available_sith, av_silver_br) | has_character_with(av_silver_br) & Has("Red Brick 2")) & (HasAllCounts({"Progressive Wallet": 4}) if using_wallets else True_()))
	#set_brick_rule(11, True_())
	set_brick_rule(12, has_grappler & has_gold_br & has_force & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(13, has_bounty_hunter & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()) & (has_republic_ship if using_ships else True_()))
	set_brick_rule(14, (has_character_with(available_sith) | Has("Red Brick 2")) & has_character_with(av_electric, av_tx20) & has_bounty_hunter) #sith, electric panels, tx-20 panels, bounty hunter though the cells DO stay unlocked so that's something
	set_brick_rule(15, has_sniper & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(16, (has_republic_ship if using_ships else True_()) & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(17, HasAllCounts({"Progressive Wallet": 1}) if using_wallets else True_())
	set_brick_rule(18, has_short & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))

	# Progressive level requirements
	if world.options.progressive_levels.value:
		# Character unlock requirements
		for level, character_list in character_level_dict.items():
			if level == "GA":
				rule = True_()
			else:
				prefix = level[0]
				level_number = int(level[1:])
				item_name = {
					"D": "Progressive Dooku",
					"V": "Progressive Ventress",
					"G": "Progressive Grievous",
				}[prefix]
				rule = (
					Has(item_name, count=level_number - 1)
					if level_number > 1
					else True_()
				)

			for character in character_list:
				location = world.multiworld.get_location(
					f"Character Unlock: {character}", player
				)
				location.access_rule = rule.resolve(world)
		for location_name in LEVEL_COMPLETION_LOCATION_IDS:
			level_name = location_name.removeprefix("Level Completed: ")

			# Only numbered Dooku, Ventress, and Grievous levels
			if (
					len(level_name) >= 2
					and level_name[0] in {"D", "V", "G"}
					and level_name[1:].isdigit()
			):
				level_number = int(level_name[1:])

				# First level is free; each later level needs
				# one more matching progressive item.
				if level_name[0] == "D":
					item_name = "Progressive Dooku"
				elif level_name[0] == "V":
					item_name = "Progressive Ventress"
				else:
					item_name = "Progressive Grievous"

				if level_number > 1:
					location = world.multiworld.get_location(
						location_name, player
					)
					location.access_rule = Has(
						item_name, count=level_number - 1
					).resolve(world)
		world.multiworld.get_location(
			"Level Completed: ZB", player
		).access_rule = HasAllCounts({
			"Progressive Dooku": 6,
			"Progressive Ventress": 6,
			"Progressive Grievous": 6,
		}).resolve(world)

	# CD and HC require a Republic ship, but only when ships are randomized.
	if world.options.randomize_ships.value:
		republic_ship_rule = HasFromListUnique(*republic_ships, count=1)

		player_locations = [
			location.name
			for location in world.multiworld.get_locations()
			if location.player == player
		]

		for level_name in ("CD", "HC"):
			location_name = f"Level Completed: {level_name}"
			location = world.multiworld.get_location(location_name, player)
			location.access_rule = republic_ship_rule.resolve(world)

	if world.options.use_minikit_characters:
		all_minikit_abilities = (
				has_force& has_dark_force& has_grappler& has_protocol& has_astromech& has_high_jump& has_hover
				& has_short& has_commander& has_clone& has_bounty_hunter& has_silver_br& has_gold_br& has_target&
				has_electric& has_sniper& has_tx20
		).resolve(world)

		for character in minikit_characters:
			location = world.multiworld.get_location(
				f"Character Unlock: {character}", player
			)
			location.access_rule = all_minikit_abilities

	if world.options.use_brig_characters:
		if world.options.progressive_levels.value:
			world.multiworld.get_location("Character Unlock: Dr. Nuvo Vindi", player).access_rule = HasAllCounts(
				{"Progressive Ventress": 2}).resolve(world)
			world.multiworld.get_location("Character Unlock: Wat Tambor", player).access_rule = HasAllCounts(
				{"Progressive Ventress": 5}).resolve(world)
			world.multiworld.get_location("Character Unlock: Lok Durd", player).access_rule = HasAllCounts(
				{"Progressive Dooku": 3}).resolve(world)
			world.multiworld.get_location("Character Unlock: Poggle the Lesser", player).access_rule = HasAllCounts(
				{"Progressive Dooku": 5}).resolve(world)
		else:
			world.multiworld.get_location("Character Unlock: Dr. Nuvo Vindi", player).access_rule = True_().resolve(
				world)
			world.multiworld.get_location("Character Unlock: Wat Tambor", player).access_rule = True_().resolve(world)
			world.multiworld.get_location("Character Unlock: Lok Durd", player).access_rule = True_().resolve(world)
			world.multiworld.get_location("Character Unlock: Poggle the Lesser", player).access_rule = True_().resolve(
				world)

		# Ground assaults; no lock implemented yet.
		world.multiworld.get_location("Character Unlock: Nute Gunray", player).access_rule = True_().resolve(world)
		world.multiworld.get_location("Character Unlock: Whorm Loathsom", player).access_rule = True_().resolve(world)