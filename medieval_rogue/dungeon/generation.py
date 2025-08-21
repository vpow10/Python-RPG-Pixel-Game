from __future__ import annotations
import random
from dataclasses import dataclass
from .room import Room, PATTERNS
from .. import settings as S
from ..entities.enemy import ENEMY_TYPES


@dataclass
class FloorPlan:
    rooms: list[Room]
    
def make_random_room(rtype: str) -> Room:
    return Room(rtype, random.choice(PATTERNS))

def generate_floor(floor_index: int) -> FloorPlan:
    n_combat = random.randint(3, 5)
    rooms = [make_random_room("combat") for _ in range(n_combat)]
    rooms.append(make_random_room("item"))
    rooms.append(make_random_room("boss"))
    return FloorPlan(rooms)

def spawn_enemies_for_room(rng: random.Random):
    count = rng.randint(S.ROOM_ENEMY_MIN, S.ROOM_ENEMY_MAX)
    picks = rng.choices(ENEMY_TYPES, k=count)
    positions = [(rng.randint(20,300), rng.randint(20,160)) for _ in range(count)]
    return [(cls, pos) for cls, pos in zip(picks, positions)]
