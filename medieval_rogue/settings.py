from __future__ import annotations


BASE_W, BASE_H = 320, 180   # logical pixels
SCALE = 4                   # window = BASE * SCALE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
DARKGRAY = (40, 40, 40)
RED = (220, 70, 70)
GREEN = (80, 200, 120)
BLUE = (80, 140, 220)
YELLOW = (240, 200, 80)

# Player base stats
PLAYER_BASE_HP = 4
PLAYER_BASE_SPEED = 80.0
PLAYER_BASE_FIRERATE = 3.0
PLAYER_BASE_PROJ_SPEED = 180.0
PLAYER_BASE_DAMAGE = 1

# Scoring
SCORE_PER_ENEMY = 10
SCORE_PER_ROOM = 25
SCORE_PER_BOSS = 200
SCORE_DECAY_PER_SEC = 1

FLOORS = 3
ROOM_ENEMY_MIN = 3
ROOM_ENEMY_MAX = 6
RANDOM_SEED = None  # set to an int for deterministic runs