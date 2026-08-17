from BaseClasses import Region, ItemClassification

from worlds.AutoWorld import World

from .Items import (
    LSW3Item,
    GAME_NAME,
    ITEM_GOLD_BRICK,
    RED_BRICK_ITEM_IDS,
    CHARACTER_ITEM_IDS,
)


class LSW3World(World):
    game = GAME_NAME

    item_name_to_id = {
        "Gold Brick": ITEM_GOLD_BRICK,
        **RED_BRICK_ITEM_IDS,
        **CHARACTER_ITEM_IDS,
    }

    item_name_to_classification = {
        "Gold Brick": ItemClassification.useful,

        **{
            name: ItemClassification.useful
            for name in RED_BRICK_ITEM_IDS
        },

        **{
            name: ItemClassification.useful
            for name in CHARACTER_ITEM_IDS
        },
    }

    location_name_to_id = {
        "Test Location": 0x4C535700 + 0x1000,
    }

    def create_regions(self):
        menu = Region(
            "Menu",
            self.player,
            self.multiworld,
        )

        self.multiworld.regions.append(menu)

    def create_items(self):
        for name in self.item_name_to_id:
            self.multiworld.itempool.append(
                self.create_item(name)
            )

    def create_item(self, name):
        return LSW3Item(
            name,
            self.item_name_to_classification[name],
            self.item_name_to_id[name],
            self.player,
        )

    def set_rules(self):
        pass

    def generate_basic(self):
        pass