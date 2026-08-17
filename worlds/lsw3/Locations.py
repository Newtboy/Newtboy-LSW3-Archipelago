from BaseClasses import Location


GAME_NAME = "LEGO Star Wars III: The Clone Wars"

BASE_ID = 0x4C535700

LOCATION_TEST = BASE_ID + 0x1000


class LSW3Location(Location):
    game = GAME_NAME