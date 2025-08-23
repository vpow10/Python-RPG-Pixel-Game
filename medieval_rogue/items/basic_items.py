from __future__ import annotations
from dataclasses import dataclass
from medieval_rogue.entities.player import Player


@dataclass
class Item:
    name: str
    apply: callable
    desc: str
    
def better_darts(player: Player): player.proj_speed *= 1.2

def longbow(player: Player): player.damage += 1

def boots(player: Player): player.speed *= 1.1

def quiver(player: Player): player.firerate *= 1.15

def chestplate(player: Player): player.hp += 1

ITEMS = [
    Item("Better Darts", better_darts, "+20% arrow speed"),
    Item("Longbow", longbow, "+1 damage"),
    Item("Boots", boots, "+10% move speed"),
    Item("Quiver", quiver, "+15% fire rate"),
    Item("Chestplate", chestplate, "+1 HP"),
]