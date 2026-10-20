from rule_builder.rules import Has, HasAllCounts, HasFromListUnique, True_
from rule_builder.rules import *
import worlds.lsw3
from rule_builder.rules import Has, HasFromListUnique
from .Locations import LEVEL_COMPLETION_LOCATION_IDS
from .ship_regions import republic_ships
from .character_regions import *


def set_rules(world: worlds.lsw3.LSW3World):
	player = world.player
	world.get_used_characters()

	world.multiworld.completion_condition[world.player] = lambda state: state.has("Level Completed: ZB", world.player)

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

	# Extra helpers due to 2 character selected limit
	av_silver_clone = av_clone & av_silver_br
	av_gold_clone = av_clone & av_gold_br
	av_electric_silver_br = av_electric & av_silver_br

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
	has_silver_clone = HasFromListUnique(*av_silver_clone, count=1)
	has_gold_clone = HasFromListUnique(*av_gold_clone, count=1)
	has_bounty_hunter = HasFromListUnique(*av_bounty_hunter, count=1)
	has_silver_br = HasFromListUnique(*av_silver_br, count=1)
	has_gold_br = HasFromListUnique(*av_gold_br, count=1)
	has_target = HasFromListUnique(*av_target, count=1)
	has_electric = HasFromListUnique(*av_electric, count=1)
	has_sniper = HasFromListUnique(*av_sniper, count=1)
	has_tx20 = HasFromListUnique(*av_tx20, count=1)

	has_republic_ship = HasFromListUnique(*republic_ships, count=1)
	has_electric_silver_br = HasFromListUnique(*av_electric_silver_br, count=1)

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
	set_brick_rule(11, has_dark_force & has_electric_silver_br & (HasAllCounts({"Progressive Wallet": 4}) if using_wallets else True_()))
	set_brick_rule(12, has_grappler & has_gold_br & has_force & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(13, has_bounty_hunter & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()) & (has_republic_ship if using_ships else True_()))
	set_brick_rule(14, (has_character_with(available_sith) | Has("Red Brick 2")) & has_character_with(av_electric, av_tx20) & has_bounty_hunter) #sith, electric panels, tx-20 panels, bounty hunter though the cells DO stay unlocked so that's something
	set_brick_rule(15, has_sniper & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(16, (has_republic_ship if using_ships else True_()) & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))
	set_brick_rule(17, HasAllCounts({"Progressive Wallet": 1}) if using_wallets else True_())
	set_brick_rule(18, has_short & (HasAllCounts({"Progressive Wallet": 2}) if using_wallets else True_()))

	# Progressive level requirements
	if world.options.progressive_levels.value:
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
					)

	# CD and HC require any Republic ship, but only when ships
	# are randomized and their unlock items are in the item pool.
	if world.options.randomize_ships.value:
		republic_ship_rule = HasFromListUnique(*republic_ships, count=1)

		for level_name in ("CD", "HC"):
			location_name = f"Level Completed: {level_name}"
			if location_name in LEVEL_COMPLETION_LOCATION_IDS:
				location = world.multiworld.get_location(
					location_name, player
				)
				location.access_rule = republic_ship_rule