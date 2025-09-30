from __future__ import annotations


# PLAN:
# floor, walls, small enemies, pickups, objects, ui icons = 32x32 pixels
# player, regular enemies = 64x64 pixels
# projectiles = 16x16 pixels, big spells 32x32 pixels
# boss sprites = 96x96 pixels, maybe 128x128 pixels


# Logical resolution and scaling
BASE_W, BASE_H = 1280, 736  # logical pixels
SCALE = 1                   # window = BASE * SCALE
FPS = 60

# Visual framing / margins
VIEW_GUTTER = 80
ROOM_INSET = 72
EDGE_FADE = 96

# Sprite / hitbox sizing
PLAYER_SPRITE_SIZE = 64
PLAYER_HITBOX = (24, 48)

ENEMY_SPRITE_SIZE = 64
ENEMY_HITBOX = (24, 48)
SMALL_ENEMY_HITBOX = (24, 24)

BOSS_SPRITE_SIZE = 96
BOSS_HITBOX = (64, 64)

PROJECTILE_SPRITE_SIZE = 16
ITEM_SPRITE_SIZE = 32

# Tile and rendering settings
TILE_SIZE = 32
SMOOTH_SCALE = False
DEBUG_DRAW_HITBOXES = False

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
DARKGRAY = (40, 40, 40)
RED = (220, 70, 70)
GREEN = (80, 200, 120)
BLUE = (80, 140, 220)
YELLOW = (240, 200, 80)
FLOOR_COLOR = (26, 22, 32)
BORDER_COLOR = (50, 40, 60)
OBSTACLES_COLOR = (60, 50, 70)
DOOR_OPEN_COLOR = (160, 130, 40)
DOOR_CLOSED_COLOR = (80, 50, 20)

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

# Generation
FLOORS = 3
ROOM_ENEMY_MIN = 3
ROOM_ENEMY_MAX = 6
RANDOM_SEED = None  # set to an int for deterministic runs, 4 -> item room up top 
SAFE_RADIUS = 192

# HUD anchoring
BORDER = 8
UI_SAFE_TOP = 0 # reserved space at top inside gutter (0 = use gutter itself)
UI_SAFE_RIGHT = 0
UI_SAFE_BOTTOM = 0
UI_SAFE_LEFT = 0

# Dungeon / Rooms
WALL_THICKNESS = 24
ROOM_CELL_W = BASE_W
ROOM_CELL_H = BASE_H
DOOR_THICKNESS = 28
DOOR_LENGTH = 72
MIN_ROOMS = 6
MAX_ROOMS = 12
DEBUG_MINIMAP = False
DEBUG_ROOMS = True

# Debug / testing
FORCE_BOSS_IN_START_ROOM = False
FORCE_BOSS_ID = None
