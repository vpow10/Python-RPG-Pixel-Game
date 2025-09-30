from __future__ import annotations
import pygame as pg, random
from dataclasses import dataclass, field
from typing import Literal, List, Tuple, Dict
from medieval_rogue import settings as S
from medieval_rogue.camera import Camera
from assets.sprite_manager import _load_image, load_strip

INSET = S.ROOM_INSET

def inset_rect(r: pg.Rect, d:int) -> pg.Rect:
    return pg.Rect(r.x + d, r.y + d, r.w - 2*d, r.h - 2*d)

RoomType = Literal["combat", "item", "boss", "start"]
Direction = Literal["N", "E", "S", "W"]

_BASE_PATTERN_W, _BASE_PATTERN_H = 320, 180
_SCALE_X = S.BASE_W / _BASE_PATTERN_W
_SCALE_Y = S.BASE_H / _BASE_PATTERN_H

RectSpec = Tuple[int, int, int, int]

# --- Patterns ---
# Keys: (room_type, w_cells, h_cells)
# NOTE: coordinates are authored in the base 320x180 logical space.
PATTERNS: Dict[Tuple[RoomType, int, int], List[List[RectSpec]]] = {
    # --- COMBAT 1x1 ---
    ("combat", 1, 1): [
        [],  # empty
        # Twin horizontal bars
        [(40, 52, 240, 12), (40, 116, 240, 12)],
        # Twin vertical pillars
        [(70, 30, 14, 120), (236, 30, 14, 120)],
        # Central block
        [(110, 56, 100, 68)],
        # Rim corridor (ring)
        [(28, 28, 264, 12), (28, 140, 264, 12), (28, 40, 12, 100), (280, 40, 12, 100)],
        # Cross
        [(150, 32, 20, 116), (64, 84, 192, 20)],
        # Four islands (near corners)
        [(48, 44, 44, 28), (228, 44, 44, 28), (48, 108, 44, 28), (228, 108, 44, 28)],
        # Staggered zig
        [(60, 40, 28, 28), (120, 70, 28, 28), (180, 100, 28, 28), (240, 130, 28, 28)],
        # twin mid bars (gap in center)
        [(40, 84, 60, 12), (220, 84, 60, 12)],
        # 4 small pillars
        [(84, 44, 24, 24), (212, 44, 24, 24), (84, 116, 24, 24), (212, 116, 24, 24)],
        # diamond lanes
        [(140, 40, 40, 20), (60, 80, 40, 20), (220, 80, 40, 20), (140, 120, 40, 20)],
        # side braces
        [(40, 40, 12, 32), (40, 108, 12, 32), (268, 40, 12, 32), (268, 108, 12, 32)],
        # twin central blocks
        [(96, 56, 40, 68), (184, 56, 40, 68)],
        # wide mid pads
        [(64, 72, 56, 36), (200, 72, 56, 36)],
    ],

    # --- COMBAT 2x1 (wide) ---
    ("combat", 2, 1): [
        [],
        # Long central bar
        [(100, 60, 420, 14)],
        # Two offset blocks
        [(160, 48, 60, 42), (420, 96, 60, 42)],
        # Wide rim corridor
        [(28, 28, 624, 12), (28, 140, 624, 12), (28, 40, 12, 100), (640, 40, 12, 100)],
        # Triple lanes
        [(80, 42, 180, 16), (80, 82, 180, 16), (80, 122, 180, 16),
         (420, 42, 180, 16), (420, 82, 180, 16), (420, 122, 180, 16)],
        # Pillar banks
        [(160, 36, 20, 36), (200, 36, 20, 36), (240, 36, 20, 36),
         (440, 108, 20, 36), (480, 108, 20, 36), (520, 108, 20, 36)],
        [(160,52,80,18),(440,110,80,18)],
        [(120,36,24,36),(200,36,24,36),(520,108,24,36),(600,108,24,36)],
        [(100,84,140,16),(440,84,140,16)],
        [(80,40,180,12),(80,128,180,12),(420,40,180,12),(420,128,180,12)],
        [(280,30,24,120)],                                         # central tower
        [(120,96,60,18),(220,60,60,18),(520,96,60,18),(420,60,60,18)],
    ],

    # --- COMBAT 1x2 (tall) ---
    ("combat", 1, 2): [
        [],
        # Two horizontal bars
        [(40, 60, 240, 14), (40, 260, 240, 14)],
        # Central tower
        [(146, 80, 28, 140)],
        # Rim corridor
        [(28, 28, 264, 12), (28, 332, 264, 12), (28, 40, 12, 292), (280, 40, 12, 292)],
        # Ladder steps
        [(60, 70, 36, 24), (100, 120, 36, 24), (140, 170, 36, 24),
         (180, 220, 36, 24), (220, 270, 36, 24)],
        [(64,96,192,16)],
        [(140,56,40,40),(140,224,40,40)],
        [(48,60,28,28),(244,60,28,28),(48,300,28,28),(244,300,28,28)],
        [(56,120,208,14),(56,240,208,14)],
        [(80,80,160,20),(80,280,160,20)],
        [(110,150,100,20)],    
    ],

    # --- COMBAT 2x2 (big) ---
    ("combat", 2, 2): [
        [],
        # Twin horizontal bars (wider)
        [(120, 100, 360, 18), (120, 260, 360, 18)],
        # Four big islands
        [(100, 80, 88, 74), (432, 80, 88, 74), (100, 208, 88, 74), (432, 208, 88, 74)],
        # Rim corridor
        [(28, 28, 624, 12), (28, 332, 624, 12), (28, 40, 12, 292), (640, 40, 12, 292)],
        # Cross with core
        [(320-12, 60, 24, 240), (120, 180-10, 400, 20), (320-28, 156, 56, 48)],
        [(120,84,160,18),(360,84,160,18),(120,276,160,18),(360,276,160,18)],
        [(160,140,80,56),(400,140,80,56)],
        [(92,92,56,56),(472,92,56,56),(92,232,56,56),(472,232,56,56)],
        [(80,60,200,16),(400,60,200,16),(80,308,200,16),(400,308,200,16)],
        [(320-18,92,36,196)],                                      # tall central
        [(160,180-10,320,20)],                                     # wide mid bar
    ],

    # --- ITEM ---
    ("item", 1, 1): [
        [],
        # Small dais/platform in middle
        [(132, 74, 56, 32)],
        # Side shelves
        [(48, 60, 32, 20), (240, 60, 32, 20), (48, 112, 32, 20), (240, 112, 32, 20)],
        [(132,64,56,20)], [(132,96,56,20)], [(92,74,20,32)], [(208,74,20,32)],
    ],

    # --- BOSS ---
    ("boss", 1, 1): [
        [],
        # Two long rails
        [(48, 48, 224, 14), (48, 118, 224, 14)],
        # Four corner pylons
        [(44, 44, 24, 24), (252, 44, 24, 24), (44, 122, 24, 24), (252, 122, 24, 24)],
        [(56,56,208,12),(56,112,208,12)],
        [(64,64,24,24),(232,64,24,24),(64,104,24,24),(232,104,24,24)],
        [(120,52,80,20),(120,104,80,20)],
    ],
    ("boss", 2, 2): [
        [],
        # Arena ring
        [(40, 40, 600, 18), (40, 322, 600, 18), (40, 58, 18, 264), (622, 58, 18, 264)],
        # Inner bumps
        [(220, 140, 40, 30), (420, 140, 40, 30), (320-20, 180-15, 40, 30)],
    ],
}

# Helpers
def _load_optional(path_parts):
    try:
        return _load_image(path_parts)
    except Exception:
        return None

_FLOOR = None
_WALLS  = None
_OBS   = None
_DOOR  = {}   # "h_open", "h_closed", "v_open", "v_closed"

def _get_tiles():
    global _FLOOR, _WALLS, _OBS, _DOOR
    
    TILE = S.TILE_SIZE
    
    if _FLOOR is None:
        try:
            _FLOOR = load_strip(['assets','sprites','tiles','floor','floor_sheet.png'], TILE, TILE)
        except Exception:
            _FLOOR = []

        try:
            _WALLS = load_strip(['assets','sprites','tiles','walls.png'], TILE, TILE)
        except Exception:
            _WALLS = []
            
        try:
            _OBS = load_strip(['assets','sprites','tiles','obstacle_sheet.png'], TILE, TILE)
        except Exception:
            _OBS = []

        _DOOR = {
            "h_open":   _load_optional(['assets','sprites','tiles','door_h_open.png']),
            "h_closed": _load_optional(['assets','sprites','tiles','door_h_closed.png']),
            "v_open":   _load_optional(['assets','sprites','tiles','door_v_open.png']),
            "v_closed": _load_optional(['assets','sprites','tiles','door_v_closed.png']),
        }
    return _FLOOR, _WALLS, _OBS, _DOOR

def _blit_tiled(surf: pg.Surface, img: pg.Surface, rect: pg.Rect):
    """Tile an image inside a *screen-space* rect."""
    tw, th = img.get_width(), img.get_height()
    start_x = rect.left - (rect.left % tw)
    start_y = rect.top  - (rect.top  % th)
    for yy in range(start_y, rect.bottom, th):
        for xx in range(start_x, rect.right, tw):
            surf.blit(img, (xx, yy))

def _variant_index_at(images: list[pg.Surface], wx: int, wy: int) -> int:
    """Choose a variant index from images based on world tile coordinate."""
    if not images:
        return 0
    tw = images[0].get_width()
    th = images[0].get_height()
    tx = wx // max(1, tw)
    ty = wy // max(1, th)
    seed = (S.RANDOM_SEED if S.RANDOM_SEED is not None else 1337)
    h = (tx * 73856093) ^ (ty * 19349663) ^ int(seed)
    if h < 0: h = -h
    return h % len(images)

def _tile_rect_world_variants(
    surf: pg.Surface,
    images: list[pg.Surface],
    rect_world: pg.Rect,
    camera: Camera | None
):
    """Tile a rect in *world coords* using per-tile variant selection that is stable by world position."""
    if not images:
        return
    tw, th = images[0].get_width(), images[0].get_height()

    start_x = rect_world.left - (rect_world.left % tw)
    start_y = rect_world.top  - (rect_world.top  % th)

    y = start_y
    while y < rect_world.bottom:
        x = start_x
        while x < rect_world.right:
            idx = _variant_index_at(images, x, y)
            img = images[idx]
            sx, sy = (x, y) if camera is None else camera.world_to_screen(x, y)

            if x + tw > rect_world.left and x < rect_world.right and y + th > rect_world.top and y < rect_world.bottom:
                surf.blit(img, (sx, sy))
            x += tw
        y += th

@dataclass
class Door:
    side: Direction
    rect: pg.Rect
    open: bool = False

@dataclass
class Room:
    kind: Room
    gx: int
    gy: int
    w_cells: int = 1
    h_cells: int = 1
    pattern: List[RectSpec] = field(default_factory=list)
    discovered: bool = False
    visited: bool = False
    cleared: bool = False
    doors: Dict[Direction, Door] = field(default_factory=dict)
    floor_map: List[List[int]] = field(default_factory=list)
    
    def __post_init__(self):
        # build a random grid of floor tile indices right away
        FLOOR, _, _, _ = _get_tiles()
        if FLOOR:
            tile_w = FLOOR[0].get_width()
            tile_h = FLOOR[0].get_height()
            room_rect = self.world_rect
            cols = room_rect.width // tile_w + 1
            rows = room_rect.height // tile_h + 1
            self.floor_map = [
                [random.randrange(len(FLOOR)) for _ in range(cols)]
                for _ in range(rows)
            ]
            
    # --- Dimensions & transforms ---
    @property
    def world_rect(self) -> pg.Rect:
        return pg.Rect(
            self.gx * S.ROOM_CELL_W,
            self.gy * S.ROOM_CELL_H,
            self.w_cells * S.ROOM_CELL_W,
            self.h_cells * S.ROOM_CELL_H,
        )

    def to_world(self, p: RectSpec) -> pg.Rect:
        x, y, w, h = p

        INTERIOR_PAD = 6
        interior = inset_rect(self.world_rect, S.ROOM_INSET + S.WALL_THICKNESS + INTERIOR_PAD)

        # Authoring canvas is 320×180 *per cell*
        base_w = _BASE_PATTERN_W * self.w_cells
        base_h = _BASE_PATTERN_H * self.h_cells

        # Scale authored rect into the interior
        sx = interior.x + int(round((x / base_w) * interior.w))
        sy = interior.y + int(round((y / base_h) * interior.h))
        sw = max(1, int(round((w / base_w) * interior.w)))
        sh = max(1, int(round((h / base_h) * interior.h)))

        r = pg.Rect(sx, sy, sw, sh)
        return r.clip(interior)

    # --- Walls ---
    def wall_rects(self) -> List[pg.Rect]:
        r = inset_rect(self.world_rect, INSET)
        b = S.WALL_THICKNESS
        walls: List[pg.Rect] = []

        # Helper to carve a gap for a door along a 1D span
        def carve_span(a0: int, a1: int, gap0: int | None, gap1: int | None) -> list[tuple[int,int]]:
            if gap0 is None or gap1 is None or gap0 >= gap1:    # no door
                return [(a0, a1)]
            segs = []
            if gap0 > a0: segs.append((a0, gap0))
            if gap1 < a1: segs.append((gap1, a1))
            return segs

        dN = self.doors.get("N"); dS = self.doors.get("S"); dW = self.doors.get("W"); dE = self.doors.get("E")

        gaps = carve_span(r.left, r.right, dN.rect.left if dN and dN.open else None, dN.rect.right if dN and dN.open else None)
        for a, b2 in gaps:
            walls.append(pg.Rect(a, r.top, b2 - a, b))
        gaps = carve_span(r.left, r.right, dS.rect.left if dS and dS.open else None, dS.rect.right if dS and dS.open else None)
        for a, b2 in gaps:
            walls.append(pg.Rect(a, r.bottom - b, b2 - a, b))
        gaps = carve_span(r.top, r.bottom, dW.rect.top if dW and dW.open else None, dW.rect.bottom if dW and dW.open else None)
        for a, b2 in gaps:
            walls.append(pg.Rect(r.left, a, b, b2 - a))
        gaps = carve_span(r.top, r.bottom, dE.rect.top if dE and dE.open else None, dE.rect.bottom if dE and dE.open else None)
        for a, b2 in gaps:
            walls.append(pg.Rect(r.right - b, a, b, b2 - a))

        for spec in self.pattern:
            walls.append(self.to_world(spec))
        return walls

    # --- Door placement ---
    def compute_doors(self, neighbours: dict[Direction, Room]) -> None:
        """
        Create door rects on sides that have neighbours.
        Door is centered on the overlapping span between this room and its neighbour.
        """
        self.doors.clear()
        my = inset_rect(self.world_rect, INSET)
        for side, nbr in neighbours.items():
            if not nbr: continue
            other = nbr.world_rect
            if side == "N":
                span_left = max(my.left, other.left)
                span_right = min(my.right, other.right)
                cx = (span_left + span_right) // 2
                rect = pg.Rect(cx - S.DOOR_LENGTH//2, my.top, S.DOOR_LENGTH, S.DOOR_THICKNESS)
            elif side == "S":
                span_left = max(my.left, other.left)
                span_right = min(my.right, other.right)
                cx = (span_left + span_right) // 2
                rect = pg.Rect(cx - S.DOOR_LENGTH//2, my.bottom - S.DOOR_THICKNESS, S.DOOR_LENGTH, S.DOOR_THICKNESS)
            elif side == "W":
                span_top = max(my.top, other.top)
                span_bottom = min(my.bottom, other.bottom)
                cy = (span_top + span_bottom) // 2
                rect = pg.Rect(my.left, cy - S.DOOR_LENGTH//2, S.DOOR_THICKNESS, S.DOOR_LENGTH)
            elif side == "E":
                span_top = max(my.top, other.top)
                span_bottom = min(my.bottom, other.bottom)
                cy = (span_top + span_bottom) // 2
                rect = pg.Rect(my.right - S.DOOR_THICKNESS, cy - S.DOOR_LENGTH//2, S.DOOR_THICKNESS, S.DOOR_LENGTH)
            self.doors[side] = Door(side=side, rect=rect, open=self.cleared or self.kind in ("start", "item"))

    # --- Drawing ---
    def draw(self, surf: pg.Surface, camera: Camera | None = None) -> None:
        def _apply(r: pg.Rect) -> pg.Rect:
            if camera is None: return r
            x, y = camera.world_to_screen(r.x, r.y)
            return pg.Rect(int(x), int(y), int(r.w), int(r.h))
                
        FLOOR, WALL, OBS, DOOR = _get_tiles()
        
        # draw floor using grid
        if FLOOR and self.floor_map:
            tile_w = FLOOR[0].get_width()
            tile_h = FLOOR[0].get_height()

            room_rect = self.world_rect
            interior = inset_rect(room_rect, INSET + S.WALL_THICKNESS)

            cols = interior.width // tile_w + 2
            rows = interior.height // tile_h + 2

            y = interior.top
            row_i = 0
            while y < interior.bottom:
                x = interior.left
                col_i = 0
                while x < interior.right:
                    idx = self.floor_map[row_i % len(self.floor_map)][col_i % len(self.floor_map[0])] if self.floor_map else 0
                    tile = FLOOR[idx]
                    rx, ry = (x, y) if camera is None else camera.world_to_screen(x, y)
                    surf.blit(tile, (rx, ry))
                    x += tile_w
                    col_i += 1
                y += tile_h
                row_i += 1
        else:
            interior = inset_rect(self.world_rect, INSET + S.WALL_THICKNESS)
            pg.draw.rect(surf, S.FLOOR_COLOR, _apply(interior))

       # walls
        walls = self.wall_rects()

        # Outer ring (first 4 rects)
        for wrect in walls[:4]:
            if WALL:
                _tile_rect_world_variants(surf, WALL, wrect, camera)
            else:
                pg.draw.rect(surf, S.BORDER_COLOR, _apply(wrect))

        # Interior obstacles/patterns (rest)
        for wrect in walls[4:]:
            # if you want obstacles to use their own sheet; fall back to WALL if OBS empty
            imgs = OBS if OBS else WALL
            if imgs:
                _tile_rect_world_variants(surf, imgs, wrect, camera)
            else:
                pg.draw.rect(surf, S.OBSTACLES_COLOR, _apply(wrect))

        # doors
        for d in self.doors.values():
            sr = _apply(d.rect)
            horizontal = (d.side in ("N","S"))
            key = ("h_" if horizontal else "v_") + ("open" if d.open else "closed")
            img = DOOR.get(key)
            if img:
                scaled = pg.transform.scale(img, (sr.w, sr.h))
                surf.blit(scaled, sr.topleft)
            else:
                color = S.DOOR_OPEN_COLOR if d.open else S.DOOR_CLOSED_COLOR
                pg.draw.rect(surf, color, sr)
