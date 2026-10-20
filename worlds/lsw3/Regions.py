import worlds.lsw3
from BaseClasses import MultiWorld, Region, Entrance, Location, ItemClassification, state
from .Locations import LSW3Location, ALL_LOCATION_TABLE, BASE_ID, studCheckLevels
from .Items import LSW3Item
from .LSW3Option import LSW3Options
from .LSW3Client.lsw3_data_pointers import LEVELS
from .character_regions import *
from rule_builder.rules import *
from .ship_regions import *

res_main = [
	"Character Unlock: Admiral Yularen",
	"Character Unlock: Clone Pilot",
	"Character Unlock: Onaconda Farr",
	"Character Unlock: Senate Commando (Captain)",
	"Red Brick Location 18"
] + [
	f"Level Completed: {name}"
	for name in LEVELS
	if name not in {"CD", "HC"}
] + [
	f"{level} Studs"
	for level in studCheckLevels
]

res_central = [
	"Character Unlock: Bail Organa",
	"Character Unlock: R6-H5",
	"Character Unlock: Sionver Boll",
	"Character Unlock: Workout Clone Trooper",
	"Red Brick Location 9",
	"Red Brick Location 11",
	"Red Brick Location 12"
]
res_medical = [
	"Character Unlock: Luxury Droid",
	"Character Unlock: MSE-6",
	"Red Brick Location 17"
]
res_minikit = [
	"Red Brick Location 5",
	"Red Brick Location 6"
] + [
	f"Character Unlock: {name}"
	for name in minikit_characters
]
res_brig = [
	"Character Unlock: Dr. Nuvo Vindi",
	"Character Unlock: Lok Durd",
	"Character Unlock: Nute Gunray",
	"Character Unlock: Poggle the Lesser",
	"Character Unlock: Wat Tambor",
	"Character Unlock: Whorm Loathsom",
	"Red Brick Location 14"
]
res_hangar = [
	"Red Brick Location 8"
]
res_gallery = [
	"Red Brick Location 3"
]
res_intersection = [
	"Character Unlock: Captain Typho",
	"Character Unlock: Queen Neeyutnee",
	"Character Unlock: Senate Commando",
	"Character Unlock: Senator Philo",
	"Red Brick Location 15"
]
res_ground_vehicle_bay = [
	"Character Unlock: Lurmen Villager",
	"Character Unlock: Senator Kharrus",
	"Character Unlock: Tee Watt Kaa"
	# The vehicles, obviously, and are NYI
]
res_landing_bay = [
	"Character Unlock: R4-P17",
	"Red Brick Location 7"
] + [
	f"Ship Unlock: {item}"
	for item in worlds.lsw3.republic_ships
]
hand_main = [
	"Character Unlock: Battle Droid",
	"Character Unlock: Cad Bane",
	"Character Unlock: Count Dooku",
	"Character Unlock: Droideka",
	"Character Unlock: Super Battle Droid",
] + [
	f"Ship Unlock: {item}"
	for item in worlds.lsw3.separatist_ships
]
hand_main_left = [ # L/R Exists for the red bricks
	"Red Brick Location 16"
]
hand_main_right = [
	"Red Brick Location 1"
]
hand_ground_vehicle_bay = [
	"Character Unlock: Gold Super Battle Droid",
	"Character Unlock: Heavy Super Battle Droid",
	"Character Unlock: LEP Servant Droid",
	"Character Unlock: Neimoidian",
	"Character Unlock: Undead Geonosian",
	"Red Brick Location 4"
	# Separatist ground vehicles
]
hand_observation_deck = [
	"Character Unlock: Asajj Ventress",
	"Level Completed: CD",
	"Red Brick Location 10"
]
hand_bridge = [
	"Character Unlock: Battle Droid Commander",
	"Character Unlock: General Grievous",
	"Character Unlock: Gonk Droid",
	"Red Brick Location 2"
]
hand_bounty_hunter = [
	"Character Unlock: Bib Fortuna",
	"Character Unlock: Gamorrean Guard",
	"Character Unlock: Geonosian Guard",
	"Character Unlock: Hondo Ohnaka",
	"Character Unlock: Jango Fett",
	"Character Unlock: Pirate Ruffian",
	"Character Unlock: Turk Falso",
	"Level Completed: HC",
	"Red Brick Location 13"
]
hand_gallery = [
	"Character Unlock: Probe Droid"
]
space = [
	# Something something gold bricks
]

regions = {
	"res_main": res_main,
	"res_central": res_central,
	"res_medical": res_medical,
	"res_minikit": res_minikit,
	"res_brig": res_brig,
	"res_hangar": res_hangar,
	"res_gallery": res_gallery,
	"res_intersection": res_intersection,
	"res_ground_vehicle_bay": res_ground_vehicle_bay,
	"res_landing_bay": res_landing_bay,
	"hand_main": hand_main,
	"hand_main_left": hand_main_left,
	"hand_main_right": hand_main_right,
	"hand_ground_vehicle_bay": hand_ground_vehicle_bay,
	"hand_observation_deck": hand_observation_deck,
	"hand_bridge": hand_bridge,
	"hand_bounty_hunter": hand_bounty_hunter,
	"hand_gallery": hand_gallery,
	"space": space
}

from collections import Counter

assigned = Counter(
	location_name
	for location_names in regions.values()
	for location_name in location_names
)

# Locations that don't exist in Locations.py
for name in sorted(assigned.keys() - ALL_LOCATION_TABLE.keys()):
	print(f"UNKNOWN LOCATION: {name}")

# Locations accidentally assigned more than once
for name, count in sorted(assigned.items()):
	if count > 1:
		print(f"DUPLICATE LOCATION ({count}x): {name}")

# Locations defined in Locations.py but not assigned to a region
for name in sorted(ALL_LOCATION_TABLE.keys() - assigned.keys()):
	print(f"UNASSIGNED LOCATION: {name}")



def create_regions(world):
	player = world.player
	multiworld = world.multiworld

	used_characters = world.get_used_characters()

	# Only characters that can appear in this world
	available_jedi = jedi & used_characters
	available_sith = sith & used_characters
	available_grapplers = grappling_hook & used_characters
	available_protocol = protocol & used_characters
	av_astromech = astromech & used_characters
	av_high_jump = high_jump & used_characters  # it's just jar jar but it's here for consistency
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
	has_dark_force = HasFromListUnique(*available_sith, count=1) | (
				Has("Red Brick 2") & HasFromListUnique(*available_jedi, count=1))
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

	# Starting region
	menu = Region("Menu", player, multiworld)
	multiworld.regions.append(menu)

	# Area regions
	for area_name in regions:
		region = Region(area_name, player, multiworld)
		multiworld.regions.append(region)

	# Connections
	connect_bidirectional(multiworld, player, "Menu", "res_main")
	connect_bidirectional(multiworld, player, "res_main", "res_central")
	connect_bidirectional(multiworld, player, "res_central", "res_medical")
	connect_bidirectional(multiworld, player, "res_central", "res_brig")
	connect_bidirectional(multiworld, player, "res_central", "res_intersection")
	connect_bidirectional(multiworld, player, "res_medical", "res_minikit")
	connect_bidirectional(multiworld, player, "res_brig", "res_hangar")
	connect_bidirectional(multiworld, player, "res_hangar", "res_gallery")
	connect_bidirectional(multiworld, player, "res_intersection", "res_ground_vehicle_bay")
	connect_bidirectional(multiworld, player, "res_intersection", "res_landing_bay")

	# Space travel
	res_to_space = connect_regions(
		multiworld, player, "res_landing_bay", "space"
	)
	hand_to_space = connect_regions(
		multiworld, player, "hand_main", "space"
	)

	# Ship requirements only apply when ships are randomized.
	if world.options.randomize_ships.value:
		res_to_space.access_rule = lambda state: any(
			state.has(ship, player)
			for ship in worlds.lsw3.republic_ships
		)

		hand_to_space.access_rule = lambda state: any(
			state.has(ship, player)
			for ship in worlds.lsw3.separatist_ships
		)

	# Returning from space is always allowed.
	connect_regions(multiworld, player, "space", "res_landing_bay")
	connect_regions(multiworld, player, "space", "hand_main")

	# Invisible Hand
	connect_bidirectional(multiworld, player, "hand_main", "hand_main_left", rule=(has_force | has_electric), return_rule="\\")
	connect_bidirectional(multiworld, player, "hand_main", "hand_main_right", rule=(has_force | has_astromech), return_rule="\\")
	connect_bidirectional(multiworld, player, "hand_main", "hand_ground_vehicle_bay")
	connect_bidirectional(multiworld, player, "hand_main_right", "hand_observation_deck")
	connect_bidirectional(multiworld, player, "hand_main_left", "hand_bridge")
	connect_bidirectional(multiworld, player, "hand_main_left", "hand_bounty_hunter",rule=(has_bounty_hunter))
	connect_bidirectional(multiworld, player, "hand_bounty_hunter", "hand_gallery")

	# Assign locations to areas
	for area_name, location_names in regions.items():
		region = multiworld.get_region(area_name, player)

		for location_name in location_names:
			location_id = ALL_LOCATION_TABLE[location_name]

			region.locations.append(LSW3Location(player, location_name, BASE_ID + location_id, region))

def connect_bidirectional(multiworld, player, a, b, rule=None, return_rule=None):
	if (return_rule == "\\"): # {
		return_rule = rule
	connect_regions(multiworld, player, a, b, rule)
	connect_regions(multiworld, player, b, a, return_rule)


def connect_regions(multiworld, player, from_, to, rule=None):
	source_region = multiworld.get_region(from_, player)
	target_region = multiworld.get_region(to, player)

	entrance = source_region.connect(
		target_region,
		f"{from_} -> {to}"
	)

	if rule is not None:
		entrance.access_rule = rule

	return entrance