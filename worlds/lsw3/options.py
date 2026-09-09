from dataclasses import dataclass

from Options import Range, PerGameCommonOptions, Toggle

class RedBrickCount(Range):
    """How many red bricks to randomize."""

    display_name = "Red Brick Count" # what shows in webhost or spoiler log

    range_start = 0
    range_end = 18
    default = 18
    
class CharacterCountPercentage(Range):
    """Percentage of Characters Randomized"""
    
    display_name = "Character Percentage"
    
    range_start = 20
    range_end = 100
    default = 50
    
class ProgressiveWallets(Toggle):
    """Progressive Wallets"""
    display_name = "Progressive Wallets"
    
class RandomizeMinikitCharacters(Toggle):
    """Randomize Minikit Characters"""
    display_name = "Randomize Minkit Characters?"
    
class RandomizeGroundBattleCharacters(Toggle):
    """Randomize Ground Battle Characters"""
    display_name = "Randomize Ground Battle Characters?"

class RandomizeBrigCharacters(Toggle):
    """Randomize Brig Characters"""
    display_name = "Randomize Brig Characters?"
    
    
@dataclass
class LSW3Options(PerGameCommonOptions):
    red_brick_count: RedBrickCount
    character_percent: CharacterCountPercentage
    progressive_wallets: ProgressiveWallets
    use_minikit_characters: RandomizeMinikitCharacters
    use_groundBattle_characters: RandomizeGroundBattleCharacters
    use_brig_characters: RandomizeBrigCharacters