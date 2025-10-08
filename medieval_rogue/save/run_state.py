from __future__ import annotations
import json, os
from typing import Any, Dict, Tuple


_DIR = os.path.dirname(__file__)
RUN_FILE = os.path.join(_DIR, "run_state.json")

def has_run_save() -> bool:
    return os.path.exists(RUN_FILE)

def clear_run_save() -> None:
    try: os.remove(RUN_FILE)
    except FileNotFoundError: pass
    
def load_run_save() -> dict | None:
    if not has_run_save(): return None
    with open(RUN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_run_state(data: Dict[str, Any]) -> None:
    os.makedirs(_DIR, exist_ok=True)
    with open(RUN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
def pack_player(player) -> dict:
    return {
        "class_id": player.cls.id if hasattr(player, "cls") else "archer",
        "hp": int(player.hp),
        "stats": {
            "hp": int(player.stats.hp),
            "damage": float(player.stats.damage),
            "speed": float(player.stats.speed),
            "firerate": float(player.stats.firerate),
            "proj_speed": float(player.stats.proj_speed),
        },
        "inventory": list(getattr(player, "inventory", [])),
    }
    
def pack_rooms(rooms: dict) -> dict:
    out = {}
    for (gx, gy), r in rooms.items():
        out[f"{gx},{gy}"] = {
            "kind": r.kind,
            "visited": bool(getattr(r, "visited", False)),
            "discovered": bool(getattr(r, "discovered", False)),
            "cleared": bool(getattr(r, "cleared", False)),
            "w_cells": int(r.w_cells),
            "h_cells": int(r.h_cells),
        }
    return out

def parse_gp(s: str) -> Tuple[int, int]:
    gx, gy = s.split(",")
    return (int(gx), int(gy))
