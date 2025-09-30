from __future__ import annotations
from typing import Dict, Callable, List, Iterable
from dataclasses import dataclass
import pygame as pg
import medieval_rogue.settings as S
import random


class Registry:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._reg: Dict[str, Callable[..., object]] = {}

    def register(self, key: str, **meta):
        def deco(cls_or_fn: Callable[..., object]):
            for k, v in meta.items():
                try:
                    setattr(cls_or_fn, k, v)
                except Exception:
                    pass
            self._reg[key] = cls_or_fn
            return cls_or_fn
        return deco

    def create(self, key: str, *args, **kwargs):
        try:
            factory = self._reg[key]
            inst = factory(*args, **kwargs)
        except KeyError as e:
            raise KeyError(f"Unknown {self.kind} kind: {key!r}. Known: {sorted(self._reg)}") from e
        if hasattr(factory, 'sprite_id'):
            from assets.sprite_manager import _load_image, slice_sheet, AnimatedSprite
            path = ['assets', 'sprites', 'enemies', f'{factory.sprite_id}_idle.png']
            try:
                img = _load_image(path)
            except FileNotFoundError:
                return inst
            inst.sprite = AnimatedSprite([img], fps=8, loop=True, anchor='bottom')
        return inst

    def keys(self) -> Iterable[str]:
        return self._reg.keys()

    def values(self):
        return self._reg.values()

    def items(self):
        return self._reg.items()

    def __len__(self):
        return len(self._reg)

    def __contains__(self, key):
        return key in self._reg


ENEMIES = Registry("enemy")
BOSSES  = Registry("boss")

register = ENEMIES.register
create   = ENEMIES.create

register_enemy = ENEMIES.register
create_enemy   = ENEMIES.create

register_boss  = BOSSES.register
create_boss    = BOSSES.create

@dataclass(frozen=True)
class Spawn:
    kind: str; rx: float; ry: float; kwargs: dict

SPAWN_PATTERNS: Dict[str, List[Spawn]] = {
    "combat_small_center": [Spawn("slime", 0.50, 0.50, {}), Spawn("slime", 0.35, 0.55, {}), Spawn("bat", 0.60, 0.45, {})],
    "combat_ring":         [Spawn("skeleton",0.50,0.20,{}), Spawn("skeleton",0.20,0.50,{}), Spawn("skeleton",0.80,0.50,{}), Spawn("bat",0.50,0.80,{})],
    "four_corners":        [Spawn("slime",0.20,0.20,{}), Spawn("slime",0.80,0.20,{}), Spawn("slime",0.20,0.80,{}), Spawn("slime",0.80,0.80,{})],
    "bats_swarm":          [Spawn("bat",0.30,0.30,{}), Spawn("bat",0.70,0.30,{}), Spawn("bat",0.30,0.70,{}), Spawn("bat",0.70,0.70,{}), Spawn("bat",0.50,0.50,{})],
    "skeleton_line":       [Spawn("skeleton",0.25,0.50,{}), Spawn("skeleton",0.40,0.50,{}), Spawn("skeleton",0.60,0.50,{}), Spawn("skeleton",0.75,0.50,{})],
    "mixed_cross":         [Spawn("slime",0.50,0.30,{}), Spawn("bat",0.30,0.50,{}), Spawn("skeleton",0.50,0.70,{}), Spawn("bat",0.70,0.50,{})],
    "zigzag":              [Spawn("bat", 0.2, 0.2, {}), Spawn("slime", 0.4, 0.4, {}), Spawn("bat", 0.6, 0.6, {}), Spawn("slime", 0.8, 0.8, {})],
    "diamond":             [Spawn("slime", 0.50, 0.25, {}), Spawn("bat",   0.25, 0.50, {}), Spawn("slime", 0.50, 0.75, {}), Spawn("bat",   0.75, 0.50, {})],
    "arc_left": [
        Spawn("skeleton", 0.20, 0.30, {}),
        Spawn("skeleton", 0.20, 0.50, {}),
        Spawn("skeleton", 0.20, 0.70, {}),
        Spawn("bat",      0.35, 0.40, {}),
        Spawn("bat",      0.35, 0.60, {}),
    ],
    "staggered_rows": [
        Spawn("slime", 0.30, 0.35, {}),
        Spawn("slime", 0.50, 0.35, {}),
        Spawn("slime", 0.70, 0.35, {}),
        Spawn("bat",   0.40, 0.55, {}),
        Spawn("bat",   0.60, 0.55, {}),
        Spawn("skeleton", 0.50, 0.75, {}),
        ],
    "pincer":      [Spawn("slime",0.20,0.50,{}), Spawn("slime",0.80,0.50,{}), Spawn("bat",0.50,0.35,{}), Spawn("bat",0.50,0.65,{})],
    "ring_dense":  [Spawn("skeleton",0.5,0.2,{}), Spawn("skeleton",0.2,0.5,{}), Spawn("skeleton",0.8,0.5,{}), Spawn("skeleton",0.5,0.8,{})],
    "cross_dense": [Spawn("bat",0.5,0.15,{}), Spawn("bat",0.15,0.5,{}), Spawn("bat",0.85,0.5,{}), Spawn("bat",0.5,0.85,{}),
                    Spawn("slime",0.5,0.5,{})],
    "wide_lanes":  [Spawn("skeleton",0.20,0.35,{}),Spawn("skeleton",0.40,0.35,{}),Spawn("skeleton",0.60,0.35,{}),Spawn("skeleton",0.80,0.35,{}),
                    Spawn("bat",0.30,0.70,{}),Spawn("bat",0.50,0.70,{}),Spawn("bat",0.70,0.70,{})],
    "tall_tiers":  [Spawn("slime",0.30,0.25,{}),Spawn("slime",0.70,0.25,{}),
                    Spawn("bat",0.50,0.50,{}),
                    Spawn("skeleton",0.30,0.75,{}),Spawn("skeleton",0.70,0.75,{})],
    "arena_big":   [Spawn("skeleton",0.25,0.25,{}),Spawn("skeleton",0.75,0.25,{}),
                    Spawn("slime",0.25,0.75,{}),Spawn("slime",0.75,0.75,{}),
                    Spawn("bat",0.50,0.50,{}),Spawn("bat",0.50,0.30,{}),Spawn("bat",0.50,0.70,{})],
}

SPAWN_BY_SIZE = {
    (1,1): ["combat_small_center","combat_ring","four_corners","mixed_cross","diamond","pincer","cross_dense"],
    (2,1): ["wide_lanes","skeleton_line","zigzag","bats_swarm","pincer"],
    (1,2): ["tall_tiers","mixed_cross","bats_swarm","zigzag","diamond"],
    (2,2): ["arena_big","ring_dense","staggered_rows","mixed_cross","bats_swarm"],
}

def pick_spawn_pattern(w_cells:int, h_cells:int, rng:random.Random) -> str:
    pool = SPAWN_BY_SIZE.get((w_cells,h_cells), list(SPAWN_PATTERNS.keys()))
    return rng.choice(pool)

def inset_rect(r: pg.Rect, d:int) -> pg.Rect:
    return pg.Rect(r.x + d, r.y + d, r.w - 2*d, r.h - 2*d)

def spawn_from_pattern(pattern_name: str, room_rect: pg.Rect, create_fn=create_enemy,
                       avoid_pos: tuple[float,float] | None = None,
                       avoid_radius: float = None) -> list:
    pattern = SPAWN_PATTERNS.get(pattern_name, [])
    INTERIOR_PAD = 12
    interior = inset_rect(room_rect, S.ROOM_INSET + S.WALL_THICKNESS + INTERIOR_PAD)

    if avoid_radius is None:
        avoid_radius = getattr(S, "SAFE_RADIUS", 160)

    ax, ay = (avoid_pos if avoid_pos is not None else (None, None))

    def too_close(x: float, y: float) -> bool:
        if ax is None:
            return False
        dx = x - ax; dy = y - ay
        return (dx*dx + dy*dy) < (avoid_radius * avoid_radius)

    out = []
    for ins in pattern:
        x = interior.left + ins.rx * interior.w
        y = interior.top  + ins.ry * interior.h

        if too_close(x, y):
            import math
            ok = False
            r = max(avoid_radius, 48)
            for tries in range(36):
                ang = (tries / 36.0) * math.tau
                jx = ax + math.cos(ang) * r
                jy = ay + math.sin(ang) * r
                jx = max(interior.left + 8, min(jx, interior.right - 8))
                jy = max(interior.top  + 8, min(jy, interior.bottom - 8))
                if not too_close(jx, jy):
                    x, y = jx, jy
                    ok = True
                    break
                r += 12

        out.append(create_fn(ins.kind, int(x), int(y), **(ins.kwargs or {})))
    return out
