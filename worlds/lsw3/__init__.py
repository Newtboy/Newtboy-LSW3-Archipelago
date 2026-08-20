from BaseClasses import Region, ItemClassification
from worlds.AutoWorld import World

from .Items import (
    LSW3Item,
    GAME_NAME,
    ITEM_GOLD_BRICK,
    RED_BRICK_ITEM_IDS,
    CHARACTER_ITEM_IDS,
    ITEM_STUDS_10,
    ITEM_STUDS_100,
    ITEM_STUDS_1000,
    ITEM_STUDS_10000
)

from .Locations import (
    LSW3Location,
    RED_BRICK_LOCATION_IDS,
)


class LSW3World(World):
    game = GAME_NAME

    item_name_to_id = {
        "Gold Brick": ITEM_GOLD_BRICK,
        **RED_BRICK_ITEM_IDS,
        **CHARACTER_ITEM_IDS,
        "10 Studs": ITEM_STUDS_10,
        "100 Studs": ITEM_STUDS_100,
        "1000 Studs": ITEM_STUDS_1000,
        "10000 Studs": ITEM_STUDS_10000
    }

    item_name_to_classification = {
        "Gold Brick": ItemClassification.useful,

        "10 Studs": ItemClassification.filler,
        "100 Studs": ItemClassification.filler,
        "1000 Studs": ItemClassification.filler,
        "10000 Studs": ItemClassification.filler,

        **{
            name: ItemClassification.useful
            for name in RED_BRICK_ITEM_IDS
        },

        **{
            name: ItemClassification.useful
            for name in CHARACTER_ITEM_IDS
        },
    }

    location_name_to_id = RED_BRICK_LOCATION_IDS

    def create_regions(self):
        menu = Region(
            "Menu",
            self.player,
            self.multiworld,
        )

        self.multiworld.regions.append(menu)

        for name, location_id in RED_BRICK_LOCATION_IDS.items():
            menu.locations.append(
                LSW3Location(
                    self.player,
                    name,
                    location_id,
                    menu,
                )
            )

    def create_items(self):
        # Add every progression/useful item.
        for name in self.item_name_to_id:
            if self.item_name_to_classification[name] != ItemClassification.filler:
                self.multiworld.itempool.append(
                    self.create_item(name)
                )

        # Fill remaining slots with random Stud values.
        filler_items = [
            "10 Studs",
            "100 Studs",
            "1000 Studs",
            "10000 Studs",
        ]

        while len(self.multiworld.itempool) < len(RED_BRICK_LOCATION_IDS):
            name = self.random.choice(filler_items)

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