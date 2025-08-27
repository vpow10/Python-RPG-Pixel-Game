from __future__ import annotations
from typing import Dict, Callable, List, Tuple


_REG: Dict[str, Callable[..., object]] = {}

def register(kind: str):
    def deco(cls_or_fn: Callable[..., object]):
        _REG[kind] = cls_or_fn
        return cls_or_fn
    return deco

def create(kind: str, *args, **kwargs):
    if kind not in _REG:
        raise KeyError(f"Unknown kind: {kind}")
    return _REG[kind](*args, **kwargs)

def available():
    return list(_REG.keys())


SPAWN_PATTERNS: Dict[str, List[Tuple[str, float, float, dict]]] = {
    "combat_small_center": [("slime", 0.5, 0.5, {}), ("slime", 0.3, 0.6, {}), ("bats", 0.4, 0.5, {}),],
    "combat_ring": [("skeleton", 0.5, 0.2, {}), ("skeleton", 0.2, 0.5,{}), ("bats", 0.4, 0.5, {})],
}

def spawn_from_pattern(pattern_name: str, room_rect, create_fn=create):
    pattern = SPAWN_PATTERNS.get(pattern_name, [])
    out = []
    for kind, rx, ry, kw in pattern:
        x = int(room_rect.left + rx * room_rect.w)
        y = int(room_rect.top + ry * room_rect.h)
        out.append(create_fn(kind, x, y, **kw))
    return out
