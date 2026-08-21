from BaseClasses import Location


GAME_NAME = "LEGO Star Wars III: The Clone Wars"

BASE_ID = 0x4C535700

RED_BRICK_LOCATION_IDS = {
    f"Red Brick Location {i}": 1000 + i
    for i in range(1, 19)
}


class LSW3Location(Location):
    game = GAME_NAME