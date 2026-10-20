from BaseClasses import MultiWorld, Region, Entrance, Location, ItemClassification
from .Locations import LSW3Location, ALL_LOCATION_TABLE, BASE_ID, studCheckLevels
from .Items import LSW3Item
from .Options import LSW3Options
from .LSW3Client.lsw3_data_pointers import LEVELS

res_main = [
    "Red Brick Location 18",
] + [
	f"Level Completed: {name}"
	for i, (name, level) in enumerate(LEVELS.items())
] + [
	f"{level} Studs"
	for level in studCheckLevels
] + [
    f"{letter}{i}"
    for letter in ("V", "G", "D")
    for i in range(1, 7)
] # Fuck you python

res_central = [

]
res_medical = [

]
res_minikit = [

]
res_brig = [

]
res_hangar = [

]
res_gallery = [

]
res_intersection = [

]
res_ground_vehicle_bay = [

]
res_landing_bay = [

]
hand_main = [

]
hand_main_left = [

]
hand_main_right = [

]
hand_ground_vehicle_bay = [

]
hand_bridge_right = [

]
hand_bridge_left = [

]
hand_bounty_hunter = [

]
hand_gallery = [

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
    "hand_bridge_right": hand_bridge_right,
    "hand_bridge_left": hand_bridge_left,
    "hand_bounty_hunter": hand_bounty_hunter,
    "hand_gallery": hand_gallery,
}

def create_regions(world):
    player = world.player
    multiworld = world.multiworld

    # Starting region
    menu = Region("Menu", player, multiworld)
    multiworld.regions.append(menu)

    # Create hub
    hub = Region("Hub", player, multiworld)
    multiworld.regions.append(hub)

    # Create level regions
    for level_name in LEVELS:
        region = Region(level_name, player, multiworld)
        multiworld.regions.append(region)

    # Create area regions
    for area_name in regions:
        region = Region(area_name, player, multiworld)
        multiworld.regions.append(region)

    # Connect Menu to Hub
    connect_regions(multiworld, player, "Menu", "Hub")

    # Connect Hub to each level
    for level_name in LEVELS:
        connect_regions(multiworld, player, "Hub", level_name)

    # Connect each level to its areas
    # TODO: Define which areas belong to which level.
    # TODO: Apply progressive-level access rules.

    # Assign locations to their areas
    for area_name, location_names in regions.items():
        region = multiworld.get_region(area_name, player)

        for location_name in location_names:
            location_id = ALL_LOCATION_TABLE[location_name]
            location = LSW3Location(
                player,
                location_name,
                BASE_ID + location_id,
                region,
            )
            region.locations.append(location)

    # Assign level-completion checks to their corresponding level regions
    for level_name in LEVELS:
        location_name = f"Level Completed: {level_name}"

        if location_name in ALL_LOCATION_TABLE:
            region = multiworld.get_region(level_name, player)
            location_id = ALL_LOCATION_TABLE[location_name]

            region.locations.append(
                LSW3Location(
                    player,
                    location_name,
                    BASE_ID + location_id,
                    region,
                )
            )


def connect_regions(multiworld, player, source, target):
    source_region = multiworld.get_region(source, player)
    target_region = multiworld.get_region(target, player)
    return source_region.connect(target_region)