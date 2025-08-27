from __future__ import annotations
from typing import Dict, Callable, List, Iterable
from dataclasses import dataclass


class Registry:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._reg: Dict[str, Callable[..., object]] = {}

    def register(self, key: str):
        def deco(cls_or_fn: Callable[..., object]):
            self._reg[key] = cls_or_fn
            return cls_or_fn
        return deco

    def create(self, key: str, *args, **kwargs):
        try:
            factory = self._reg[key]
        except KeyError as e:
            raise KeyError(f"Unknown {self.kind} kind: {key!r}. Known: {sorted(self._reg)}") from e
        return factory(*args, **kwargs)

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
}

def spawn_from_pattern(pattern_name: str, room_rect, create_fn=create_enemy):
    pattern = SPAWN_PATTERNS.get(pattern_name, [])
    out = []
    for ins in pattern:
        x = int(room_rect.left + ins.rx * room_rect.w)
        y = int(room_rect.top  + ins.ry * room_rect.h)
        out.append(create_fn(ins.kind, x, y, **(ins.kwargs or {})))
    return out
