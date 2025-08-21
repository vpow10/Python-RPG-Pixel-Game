from __future__ import annotations
import json, os
SAVE_FILE = os.path.join(os.path.dirname(__file__), "highscores.json")


def load_highscores():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except FileNotFoundError: return []

def save_highscore(name: str, score: int):
    scores = load_highscores()
    scores.append({"name": (name or "YOU")[:8].upper(), "score": int(score)})
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:10]
    with open(SAVE_FILE, "w", encoding="utf-8") as f: json.dump(scores, f, indent=2)
