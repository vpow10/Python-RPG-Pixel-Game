from dataclasses import dataclass
from typing import Dict, Callable

@dataclass
class PlayerClass:
    id: str
    name: str
    hp: int
    damage: float
    speed: float
    firerate: float
    proj_speed: float
    description: str = ""
    special: Callable = None  # optional special ability hook


# Registry
PLAYER_CLASSES: Dict[str, PlayerClass] = {}


def register_player_class(cls: PlayerClass):
    """Register a new player class by id."""
    if cls.id in PLAYER_CLASSES:
        raise ValueError(f"Player class '{cls.id}' already registered")
    PLAYER_CLASSES[cls.id] = cls
    return cls


# --- Example classes ---
register_player_class(
    PlayerClass(
        id="archer",
        name="Archer",
        hp=5,
        damage=1,
        speed=220.0,
        firerate=3.0,
        proj_speed=280.0,
        description="Balanced class with strong DPS.",
    )
)

register_player_class(
    PlayerClass(
        id="rogue",
        name="Rogue",
        hp=4,
        damage=2,
        speed=250.0,
        firerate=2.0,
        proj_speed=190.0,
        description="Fast and agile, but fragile.",
    )
)

register_player_class(
    PlayerClass(
        id="mage",
        name="Mage",
        hp=3,
        damage=3,
        speed=190.0,
        firerate=1.3,
        proj_speed=160.0,
        description="Powerful projectiles, but slow cast.",
    )
)
