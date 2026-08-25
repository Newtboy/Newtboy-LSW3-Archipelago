from BaseClasses import Location
from .Characters import CHARACTERS as ch

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

studCheckLevels = [
    10000,
    100000,
    1000000,
]

STUD_LOCATION_IDS = {
    f"{level} Studs": 4000 + i
    for i, level in enumerate(studCheckLevels)
}

class LSW3Location(Location):
    game = GAME_NAME