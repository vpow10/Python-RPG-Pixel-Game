from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from medieval_rogue.entities.player import Player

@dataclass(frozen=True)
class Item:
    name: str; apply: Callable[[Player], None]; desc: str

def better_darts(p: Player) -> None: p.proj_speed *= 1.2
def longbow(p: Player) -> None: p.damage += 1
def boots(p: Player) -> None: p.speed *= 1.1
def quiver(p: Player) -> None: p.firerate *= 1.15
def chestplate(p: Player) -> None: p.hp += 1

ITEMS = [
    Item("Better Darts", better_darts, "+20% arrow speed"),
    Item("Longbow", longbow, "+1 damage"),
    Item("Boots", boots, "+10% move speed"),
    Item("Quiver", quiver, "+15% fire rate"),
    Item("Chestplate", chestplate, "+1 HP"),
]

_item_map = {it.name: it for it in ITEMS}

def get_item_by_name(name: str) -> Item | None:
    return _item_map.get(name)
