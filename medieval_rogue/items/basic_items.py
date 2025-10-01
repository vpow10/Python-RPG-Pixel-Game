from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from medieval_rogue.entities.player import Player

@dataclass(frozen=True)
class Item:
    name: str; apply: Callable[[Player], None]; desc: str

def better_arrows(p: Player) -> None: p.stats.proj_speed *= 1.2
def projectile_ring(p: Player) -> None: p.stats.proj_speed *= 1.2
def longbow(p: Player) -> None: p.stats.damage += 1
def strength_potion(p: Player) -> None: p.stats.damage += 1
def speed_boots(p: Player) -> None: p.stats.speed *= 1.1
def quiver(p: Player) -> None: p.stats.firerate *= 1.15
def gloves(p: Player) -> None: p.stats.firerate *= 1.15
def chestplate(p: Player) -> None: p.stats.hp += 1

ITEMS = [
    # Item("Better Arrows", better_arrows, "+20% arrow speed"),
    Item("Gloves", gloves, "+15% fire rate"),
    Item("Speed Boots", speed_boots, "+10% move speed"),
    Item("Strength Potion", strength_potion, "+1 damage"),
    Item("Projectile Ring", projectile_ring, "+20% projectile speed"),
    # Item("Longbow", longbow, "+1 damage"),
    # Item("Quiver", quiver, "+15% fire rate"),
    Item("Chestplate", chestplate, "+1 HP"),
]

_item_map = {it.name: it for it in ITEMS}

def get_item_by_name(name: str) -> Item | None:
    return _item_map.get(name)
