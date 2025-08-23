import pygame as pg

def load_sounds():
    return {
        "shot": pg.mixer.Sound("medieval_rogue/assets/sfx/arrow_shot.wav"),
        "player_hit": pg.mixer.Sound("medieval_rogue/assets/sfx/player_hit.wav"),
        # "kill": pg.mixer.Sound("assets/sfx/kill.wav"),
    }
