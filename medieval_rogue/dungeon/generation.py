from __future__ import annotations
import random, math, collections
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from medieval_rogue.dungeon.room import Room, PATTERNS, RoomType, Direction
from medieval_rogue import settings as S

GridPos = Tuple[int, int]

DIRS: dict[Direction, Tuple[int, int]] = {
    "N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)
}
OPP: dict[Direction, Direction] = {"N":"S", "S":"N", "W":"E", "E":"W"}

@dataclass
class FloorPlan:
    rooms: Dict[GridPos, Room]
    start: GridPos

# --- Helpers ---

def _weighted_size_roll(rng: random.Random) -> Tuple[int, int]:
    roll = rng.random()
    if roll < 0.05:
        return (2, 2)
    elif roll < 0.2:
        return (2, 1)
    elif roll < 0.4:
        return (1, 2)
    return (1, 1)


def _grow_tree(rng: random.Random, target_rooms: int) -> dict[GridPos, tuple[int,int]]:
    placed: dict[GridPos, tuple[int,int]] = {(0,0): (1, 1)}     # start room is 1x1
    frontier: list[GridPos] = [(0,0)]
    attempts = 0
    while len(placed) < target_rooms and attempts < target_rooms * 40:
        attempts += 1
        gx, gy = rng.choice(frontier)
        dx, dy = rng.choice(list(DIRS.values()))
        cand = (gx + dx, gy + dy)
        if cand in placed: continue
        w, h = _weighted_size_roll(rng)
        occupied = False
        for x in range(cand[0], cand[0] + w):
            for y in range(cand[1], cand[1] + h):
                if (x, y) in placed:
                    occupied = True
                    break
            if occupied: break
        if occupied: continue
        placed[cand] = (w, h)
        frontier.append(cand)
    return placed


def _graph_neighbours(rooms: dict[GridPos, Room]) -> dict[GridPos, dict[Direction, Optional[Room]]]:
    out: dict[GridPos, dict[Direction, Optional[Room]]] = {}
    for (gx, gy), r in rooms.items():
        nbrs: dict[Direction, Optional[Room]] = {"N": None, "S": None, "W": None, "E": None}
        for side, (dx, dy) in DIRS.items():
            for x in range(r.w_cells):
                for y in range(r.h_cells):
                    cx = gx + x + dx
                    cy = gy + y + dy
                    if (cx, cy) in rooms:
                        nbrs[side] = rooms[(cx, cy)]
                        break
                if nbrs[side]: break
        out[(gx, gy)] = nbrs
    return out


def _farthest_leaf(start: GridPos, neighbours: dict[GridPos, dict[Direction, Optional[Room]]]) -> GridPos:
    q = collections.deque([start])
    dist = {start: 0}
    parent = {start: None}
    far = start
    while q:
        cur = q.popleft()
        if dist[cur] >= dist[far]:
            far = cur
        for side, nbr in neighbours[cur].items():
            if not nbr: continue
            gp = (nbr.gx, nbr.gy)
            if gp not in dist:
                dist[gp] = dist[cur] + 1
                parent[gp] = cur
                q.append(gp)
    return far


def _pick_item_leaf(
        rng: random.Random, start: GridPos, boss_at: GridPos, neighbours: dict[GridPos, dict[Direction, Optional[Room]]]) -> GridPos:
    leaves = []
    for gp, nbrs in neighbours.items():
        if gp in (start, boss_at):
            continue
        if sum(1 for n in nbrs.values() if n) <= 1:
            leaves.append(gp)
    if not leaves:
        candidates = [gp for gp in neighbours.keys() if gp not in (start, boss_at)]
        return rng.choice(candidates) if candidates else start
    return rng.choice(leaves)

# --- Floor generation ---

def generate_floor(floor_index: int, rng: Optional[random.Random] = None) -> FloorPlan:
    rng = rng or random.Random(S.RANDOM_SEED)
    n_rooms = rng.randint(S.MIN_ROOMS, S.MAX_ROOMS)

    sizes = _grow_tree(rng, n_rooms)
    rooms: dict[GridPos, Room] = {}
    for (gx, gy), (w, h) in sizes.items():
        kind: RoomType = "start" if (gx, gy) == (0, 0) else "combat"
        pats = PATTERNS.get(("combat", w, h), [[ ]]) if kind != "start" else [[ ]]
        pattern = rng.choice(pats)
        rooms[(gx, gy)] = Room(kind=kind, gx=gx, gy=gy, w_cells=w, h_cells=h, pattern=pattern)

    neighbours = _graph_neighbours(rooms)

    # Assign boss + item
    boss_at = _farthest_leaf((0,0), neighbours)
    rooms[boss_at].kind = "boss"
    boss_pats = PATTERNS.get(("boss", rooms[boss_at].w_cells, rooms[boss_at].h_cells))
    if boss_pats:
        rooms[boss_at].pattern = rng.choice(boss_pats)

    item_at = _pick_item_leaf(rng, (0,0), boss_at, neighbours)
    rooms[item_at].kind = "item"
    item_pats = PATTERNS.get(("item", rooms[item_at].w_cells, rooms[item_at].h_cells))
    if item_pats:
        rooms[item_at].pattern = rng.choice(item_pats)

    for gp, room in rooms.items():
        room.compute_doors(neighbours[gp])

    return FloorPlan(rooms=rooms, start=(0,0))
