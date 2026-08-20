import dolphin_memory_engine as dme

from . import lsw3_data_pointers as ld


class LSW3Memory:
    STUDS = ld.STUD_COUNT
    GOLD_BRICKS = ld.GOLD_BRICK_COUNT

    RED_BRICKS_1_8 = ld.RED_BRICKS_1_8
    RED_BRICKS_9_16 = ld.RED_BRICKS_9_16
    RED_BRICKS_17_18 = ld.RED_BRICKS_17_18

    RED_BRICK_1_8_COUNT = ld.RED_BRICK_1_8_COUNT
    RED_BRICK_9_16_COUNT = ld.RED_BRICK_9_16_COUNT
    RED_BRICK_17_18_COUNT = ld.RED_BRICK_17_18_COUNT

    CHEAT_CODE_CHARACTERS = ld.CHEAT_CODE_CHARACTERS
    CHEAT_CODE_CURSOR_INDEX = ld.CHEAT_CODE_CURSOR_INDEX

    CHARACTERS = dict(ld.UNNAMED_GROUP)

    def __init__(self):
        dme.hook()

        if not dme.is_hooked():
            raise RuntimeError("Could not hook Dolphin.")

    def read_bytes(self, address, size):
        return dme.read_bytes(address, size)

    def write_bytes(self, address, data):
        dme.write_bytes(address, data)

    def read_u8(self, address):
        return int.from_bytes(
            self.read_bytes(address, 1),
            byteorder="big",
            signed=False
        )

    def write_u8(self, address, value):
        if not 0 <= value <= 0xFF:
            raise ValueError("u8 value out of range")

        self.write_bytes(
            address,
            value.to_bytes(1, byteorder="big", signed=False)
        )

    def read_u64(self, address):
        return int.from_bytes(
            self.read_bytes(address, 8),
            byteorder="big",
            signed=False
        )

    def write_u64(self, address, value):
        if not 0 <= value <= 0xFFFFFFFFFFFFFFFF:
            raise ValueError("u64 value out of range")

        self.write_bytes(
            address,
            value.to_bytes(8, byteorder="big", signed=False)
        )

    @property
    def studs(self):
        return self.read_u64(self.STUDS)

    @studs.setter
    def studs(self, value):
        self.write_u64(self.STUDS, value)

    @property
    def gold_bricks(self):
        return self.read_u8(self.GOLD_BRICKS)

    @gold_bricks.setter
    def gold_bricks(self, value):
        self.write_u8(self.GOLD_BRICKS, value)

    @property
    def red_bricks_1_8(self):
        return self.read_u8(self.RED_BRICKS_1_8)

    @red_bricks_1_8.setter
    def red_bricks_1_8(self, value):
        self.write_u8(self.RED_BRICKS_1_8, value)

    @property
    def red_bricks_9_16(self):
        return self.read_u8(self.RED_BRICKS_9_16)

    @red_bricks_9_16.setter
    def red_bricks_9_16(self, value):
        self.write_u8(self.RED_BRICKS_9_16, value)

    @property
    def red_bricks_17_18(self):
        return self.read_u8(self.RED_BRICKS_17_18)

    @red_bricks_17_18.setter
    def red_bricks_17_18(self, value):
        self.write_u8(self.RED_BRICKS_17_18, value)

    @property
    def red_brick_1_8_count(self):
        return self.read_u8(self.RED_BRICK_1_8_COUNT)

    @red_brick_1_8_count.setter
    def red_brick_1_8_count(self, value):
        self.write_u8(self.RED_BRICK_1_8_COUNT, value)

    @property
    def red_brick_9_16_count(self):
        return self.read_u8(self.RED_BRICK_9_16_COUNT)

    @red_brick_9_16_count.setter
    def red_brick_9_16_count(self, value):
        self.write_u8(self.RED_BRICK_9_16_COUNT, value)

    @property
    def red_brick_17_18_count(self):
        return self.read_u8(self.RED_BRICK_17_18_COUNT)

    @red_brick_17_18_count.setter
    def red_brick_17_18_count(self, value):
        self.write_u8(self.RED_BRICK_17_18_COUNT, value)

    def get_character(self, name):
        return self.read_u8(self.CHARACTERS[name])

    def set_character(self, name, value):
        self.write_u8(self.CHARACTERS[name], value)

    def character_unlocked(self, name):
        return self.get_character(name) != 0

    def unlock_character(self, name):
        if name not in self.CHARACTERS:
            raise KeyError(f"Unknown character: {name}")

        self.set_character(name, 1)

    def lock_character(self, name):
        self.set_character(name, 0)
        
    def reset_managed_state(self):
        # Red Bricks
        self.red_bricks_1_8 = 0
        self.red_bricks_9_16 = 0
        self.red_bricks_17_18 = 0

        self.red_brick_1_8_count = 0
        self.red_brick_9_16_count = 0
        self.red_brick_17_18_count = 0

        # Gold Bricks
        self.gold_bricks = 0

        # Characters
        for name in self.CHARACTERS:
            self.lock_character(name)

    def unlock_red_brick(self, brick_number):
        if not 1 <= brick_number <= 18:
            raise ValueError("Red brick number must be between 1 and 18")

        if brick_number <= 8:
            flags_address = self.RED_BRICKS_1_8
            count_address = self.RED_BRICK_1_8_COUNT
            bit = 1 << (brick_number - 1)

        elif brick_number <= 16:
            flags_address = self.RED_BRICKS_9_16
            count_address = self.RED_BRICK_9_16_COUNT
            bit = 1 << (brick_number - 9)

        else:
            flags_address = self.RED_BRICKS_17_18
            count_address = self.RED_BRICK_17_18_COUNT
            bit = 1 << (brick_number - 17)

        flags = self.read_u8(flags_address)

        # Already unlocked.
        if flags & bit:
            return False

        flags |= bit

        self.write_u8(flags_address, flags)

        # Keep the pause-menu count synchronized.
        self.write_u8(
            count_address,
            flags.bit_count()
        )

        return True

    def lock_red_brick_unlock_flag(self, brick_number):
        """Clear the actual red-brick unlock flag."""
        if not 1 <= brick_number <= 18:
            raise ValueError("Red brick number must be between 1 and 18")

        if brick_number <= 8:
            address = self.RED_BRICKS_1_8
            bit = 1 << (brick_number - 1)

        elif brick_number <= 16:
            address = self.RED_BRICKS_9_16
            bit = 1 << (brick_number - 9)

        else:
            address = self.RED_BRICKS_17_18
            bit = 1 << (brick_number - 17)

        current = self.read_u8(address)

        if not current & bit:
            return False

        self.write_u8(address, current & ~bit)

        return True
    
    def lock_red_brick_count(self, brick_number):
        """Remove this brick from the game's displayed collected count."""
        if not 1 <= brick_number <= 18:
            raise ValueError("Red brick number must be between 1 and 18")

        if brick_number <= 8:
            address = self.RED_BRICK_1_8_COUNT

        elif brick_number <= 16:
            address = self.RED_BRICK_9_16_COUNT

        else:
            address = self.RED_BRICK_17_18_COUNT

        current = self.read_u8(address)

        if current == 0:
            return False

        self.write_u8(address, current - 1)

        return True
