from enum import Enum
import random

class MonsterType(Enum):
    FIRE = "Fire"
    ICE = "Ice"
    ELECTRIC = "Electric"
    EARTH = "Earth"
    WIND = "Wind"
    TOXIC = "Toxic"
    MECHANICAL = "Mechanical"
    CRYSTAL = "Crystal"

class MonsterAbility:
    def __init__(self, name, description, damage, cooldown, effect_type):
        self.name = name
        self.description = description
        self.damage = damage
        self.cooldown = cooldown
        self.effect_type = effect_type

class MonsterTrait:
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect

# Monster Abilities Database
MONSTER_ABILITIES = {
    "Fireball": MonsterAbility(
        "Fireball",
        "Launches a ball of fire that explodes on impact",
        30,
        2000,
        MonsterType.FIRE
    ),
    "Frost Nova": MonsterAbility(
        "Frost Nova",
        "Creates an expanding ring of ice that slows enemies",
        20,
        3000,
        MonsterType.ICE
    ),
    "Lightning Strike": MonsterAbility(
        "Lightning Strike",
        "Calls down a bolt of lightning that chains between enemies",
        40,
        4000,
        MonsterType.ELECTRIC
    ),
    "Earth Spike": MonsterAbility(
        "Earth Spike",
        "Summons spikes from the ground",
        25,
        2500,
        MonsterType.EARTH
    ),
    "Wind Slash": MonsterAbility(
        "Wind Slash",
        "Creates a cutting wind that passes through enemies",
        15,
        1500,
        MonsterType.WIND
    ),
    "Poison Cloud": MonsterAbility(
        "Poison Cloud",
        "Releases a cloud of toxic gas that damages over t