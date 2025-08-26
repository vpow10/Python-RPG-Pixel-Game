from __future__ import annotations
import pygame as pg
from dataclasses import dataclass, field
from typing import Literal, List, Tuple, Dict
from medieval_rogue import settings as S


RoomType = Literal["combat", "item", "boss", "start"]
Direction = Literal["N", "E", "S", "W"]

_BASE_PATTERN_W, _BASE_PATTERN_H = 320, 180
_SCALE_X = S.BASE_W / _BASE_PATTERN_W
_SCALE_Y = S.BASE_H / _BASE_PATTERN_H

RectSpec = Tuple[int, int, int, int]

# --- Patterns ---
# Keys: (room_type, w_cells, h_cells)
PATTERNS: Dict[Tuple[RoomType, int, int], List[List[RectSpec]]] = {
    ("combat", 1, 1): [
        [],     # empty
        [(40, 40, 240, 12), (40, 128, 240, 12)],    # two horizontal bars
        [(60, 30, 12, 120), (248, 30, 12, 120)],    # two pillars
        [(110, 60, 100, 60)],                       # central block
    ],
    ("combat", 2, 1): [
        [],
        [(100, 40, 420, 12)],
        [(260, 60, 40, 60)],
    ],
    ("combat", 1, 2): [
        [],
        [(40, 40, 240, 12), (40, 128, 240, 12)],
        [(60, 30, 12, 120), (248, 30, 12, 120)],
        [(110, 60, 100, 60)],
    ],
    ("combat", 2, 2): [
        [],
        [(120, 90, 360, 20), (120, 270, 360, 20)],
        [(80, 80, 90, 90), (430, 80, 90, 90), (80, 210, 90, 90), (430, 210, 90, 90)],
    ],
    ("item", 1, 1): [
        [],
        [(120, 70, 80, 40)],
    ],
    ("boss", 1, 1): [
        [],
        [(60, 40, 200, 12), (60, 128, 200, 12)],
    ],
    ("boss", 2, 2): [
        [],
        [(160, 100, 280, 20), (160, 260, 280, 20)],
    ],
}

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
        # Scale pattern per cell block; pattern is authored for 1x1, so tile across
        sx = int(round(x * _SCALE_X))
        sy = int(round(y * _SCALE_Y))
        sw = int(round(w * _SCALE_X))
        sh = int(round(h * _SCALE_Y))
        return pg.Rect(self.world_rect.x + sx, self.world_rect.y + sy, sw, sh)

    # --- Walls ---
    def wall_rects(self) -> List[pg.Rect]:
        r = self.world_rect
        b = S.BORDER
        walls: List[pg.Rect] = [
            pg.Rect(r.left, r.top, r.w, b),  # top
            pg.Rect(r.left, r.bottom - b, r.w, b),  # bottom
            pg.Rect(r.left, r.top, b, r.h),  # left
            pg.Rect(r.right - b, r.top, b, r.h),  # right
        ]
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
        my = self.world_rect
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
        def draw(self, surf: pg.Surface) -> None:
            pg.draw.rect(surf, S.FLOOR_COLOR, self.world_rect)
            for w in self.wall_rects()[:4]:
                pg.draw.rect(surf, S.BORDER_COLOR, w)
            for w in self.wall_rects()[4:]:
                pg.draw.rect(surf, S.OBSTACLES_COLOR, w)
            for d in self.doors.values():
                color = S.DOOR_OPEN_COLOR if d.open else S.DOOR_CLOSED_COLOR
                pg.draw.rect(surf, color, d.rect)
