from dataclasses import dataclass
from typing import Dict, Callable

@dataclass
class PlayerClass:
    id: str
    name: str
    max_hp: int
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
        max_hp=5,
        damage=1,
        speed=220.0,
        firerate=3.0,
        proj_speed=200.0,
        description="Balanced class with strong DPS.",
    )
)

register_player_class(
    PlayerClass(
        id="rogue",
        name="Rogue",
        max_hp=4,
        damage=2,
        speed=240.0,
        firerate=2.0,
        proj_speed=120.0,
        description="Fast and agile, but fragile.",
    )
)

register_player_class(
    PlayerClass(
        id="mage",
        name="Mage",
        max_hp=3,
        damage=3,
        speed=180.0,
        firerate=1.3,
        proj_speed=100.0,
        description="Powerful projectiles, but slow cast.",
    )
)
