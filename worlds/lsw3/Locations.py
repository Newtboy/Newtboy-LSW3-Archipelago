from BaseClasses import Location


GAME_NAME = "LEGO Star Wars III: The Clone Wars"

BASE_ID = 0x4C535700


RED_BRICK_LOCATION_IDS = {
    f"Red Brick {i}": BASE_ID + 0x1000 + (i - 1)
    for i in range(1, 19)
}


class LSW3Location(Location):
    game = GAME_NAME