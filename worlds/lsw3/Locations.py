from BaseClasses import Location
from .Characters import CHARACTERS as ch
from .Ships import SHIPS as Ships
from .LSW3Client.lsw3_data_pointers import LEVELS

GAME_NAME = "LEGO Star Wars III: The Clone Wars"

BASE_ID = 0x4C535700

RED_BRICK_LOCATION_IDS = {
	f"Red Brick Location {i}": 1000 + i
	for i in range(1, 19)
}

CHARACTER_LOCATION_IDS = {
	f"Character Unlock: {item}": 2000 + i
	for i, item in enumerate(ch, start=1)
}

SHIP_LOCATION_IDS = {
	f"Ship Unlock: {item}": 3000 + i
	for i, item in enumerate(Ships, start=1)
}

studCheckLevels = [
	10_000,
	100_000,
	1_000_000,
	10_000_000,
	100_000_000
]

STUD_LOCATION_IDS = {
	f"{level} Studs": 4000 + i
	for i, level in enumerate(studCheckLevels)
}


LEVEL_COMPLETION_LOCATION_IDS = {
	# Level COMPLETION
	f"Level Completed: {name}": 5000 + i
	for i, (name, level) in enumerate(LEVELS.items())
	# if name != "D1" and name != "V1" and name != "G1" and name != "GA" and name != "ZB"
	# if name != "CD" and name != "HC" # Genuinely what am I doing atp
}

ALL_LOCATION_TABLE = {
	**RED_BRICK_LOCATION_IDS,
	**CHARACTER_LOCATION_IDS,
	**SHIP_LOCATION_IDS,
	**STUD_LOCATION_IDS,
	**LEVEL_COMPLETION_LOCATION_IDS
}

class LSW3Location(Location):
	game = GAME_NAME