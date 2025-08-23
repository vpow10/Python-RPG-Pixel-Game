import pygame as pg
from medieval_rogue.utils import resource_path

def load_sounds():
    return {
        "shot": pg.mixer.Sound(resource_path("assets", "sfx", "arrow_shot.wav")),
        "player_hit": pg.mixer.Sound(resource_path("assets", "sfx", "player_hit.wav")),
        # "kill": pg.mixer.Sound(resource_path("assets", "sfx", "kill.wav")),
    }