from __future__ import annotations
import random
from dataclasses import dataclass
from medieval_rogue.dungeon.room import Room, PATTERNS, BOSS_PATTERNS
from medieval_rogue import settings as S
from medieval_rogue.entities.enemy import ENEMY_TYPES
from medieval_rogue.entities.player import Player
import math


@dataclass
class FloorPlan:
    rooms: list[Room]
    
def make_random_room(rtype: str) -> Room:
    if rtype == "boss":
        return Room(rtype, random.choice(BOSS_PATTERNS))
    else:
        return Room(rtype, random.choice(PATTERNS))

def generate_floor(floor_index: int) -> FloorPlan:
    n_combat = random.randint(3, 5)
    rooms = [make_random_room("combat") for _ in range(n_combat)]
    rooms.append(make_random_room("item"))
    rooms.append(make_random_room("boss"))
    rooms.append(make_random_room("item"))
    return FloorPlan(rooms)

def spawn_enemies_for_room(rng: random.Random, player: Player):
    count = rng.randint(S.ROOM_ENEMY_MIN, S.ROOM_ENEMY_MAX)
    picks = rng.choices(ENEMY_TYPES, k=count)
    enemies_count = 0
    positions = []
    while enemies_count < count:
        position = (rng.randint(20,300), rng.randint(20,160))
        if math.dist(position, player.center()) > S.SAFE_RADIUS:
            positions.append(position)
            enemies_count += 1
    return [(cls, pos) for cls, pos in zip(picks, positions)]
