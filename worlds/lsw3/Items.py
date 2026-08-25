from BaseClasses import Item

from .Characters import CHARACTERS

GAME_NAME = "LEGO Star Wars III: The Clone Wars"

BASE_ID = 0x4C535700

# Trap
# NYI

# Junk
ITEM_STUDS_10 = BASE_ID + 0x0300
ITEM_STUDS_100 = BASE_ID + 0x0301
ITEM_STUDS_1000 = BASE_ID + 0x0302
ITEM_STUDS_10000 = BASE_ID + 0x0303

ITEM_PROGRESSIVE_WALLET = BASE_ID + 0x0400

# Progression
ITEM_GOLD_BRICK = BASE_ID + 0x0001

# Red Bricks
RED_BRICK_ITEM_IDS = {
    f"Red Brick {i}": BASE_ID + 0x0200 + i
    for i in range(1, 19)
}

# Characters
CHARACTER_ITEM_IDS = {
    name: BASE_ID + 0x0100 + index
    for index, name in enumerate(CHARACTERS)
}


class LSW3Item(Item):
    game = GAME_NAME