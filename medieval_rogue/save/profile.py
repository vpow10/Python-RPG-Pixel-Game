from __future__ import annotations
import json, os
from typing import Dict, Any


_DIR = os.path.dirname(__file__)
PROFILE_FILE = os.path.join(_DIR, "profile.json")

_DEFAULT = {
    "stats": {
        "runs_started": 0,
        "runs_won": 0,
        "bosses_defeated": 0,
        "rooms_cleared": 0,
        "archer_wins": 0,
    },
    "unlocks": {
        "knight": False,
    }
}

def load_profile() -> Dict[str, Any]:
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    out = _DEFAULT.copy()
    out["stats"] = {**_DEFAULT["stats"], **data.get("stats", {})}
    out["unlocks"] = {**_DEFAULT["unlocks"], **data.get("unlocks", {})}
    return out

def save_profile(p: Dict[str, Any]) -> None:
    os.makedirs(_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)
        
def bump_stat(key: str, delta: int = 1) -> None:
    p = load_profile()
    p["stats"][key] = int(p["stats"].get(key, 0)) + int(delta)
    save_profile(p)

def set_unlock(class_id: str, value: bool = True) -> None:
    p = load_profile()
    p["unlocks"][class_id] = bool(value)
    save_profile(p)
    
def is_unlocked(class_id: str) -> bool:
    p = load_profile()
    return bool(p["unlocks"].get(class_id, False))

def record_run_started() -> None:
    bump_stat("runs_started", 1)
    
def record_boss_defeated() -> None:
    bump_stat("bosses_defeated", 1)

def record_room_cleared() -> None:
    bump_stat("rooms_cleared", 1)

def record_run_finished(win: bool, class_id: str) -> None:
    if win:
        bump_stat("runs_won", 1)
        if class_id == "archer":
            bump_stat("archer_wins", 1)
            set_unlock("knight", True)
