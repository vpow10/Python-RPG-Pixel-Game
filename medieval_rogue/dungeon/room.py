from __future__ import annotations
import pygame as pg
from dataclasses import dataclass, field
from typing import Literal, List, Tuple, Dict
from medieval_rogue import settings as S
from medieval_rogue.camera import Camera


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
        r = self.world_rect; b = S.BORDER
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
    def draw(self, surf: pg.Surface, camera: Camera | None = None) -> None:
        def _apply(r: pg.Rect) -> pg.Rect:
            if camera is None: return r
            x, y = camera.world_to_screen(r.x, r.y)
            return pg.Rect(int(x), int(y), int(r.w), int(r.h))

        pg.draw.rect(surf, S.FLOOR_COLOR, _apply(self.world_rect))

        walls = self.wall_rects()
        for w in walls[:4]:
            pg.draw.rect(surf, S.BORDER_COLOR, _apply(w))
        for w in walls[4:]:
            pg.draw.rect(surf, S.OBSTACLES_COLOR, _apply(w))
        for d in self.doors.values():
            color = S.DOOR_OPEN_COLOR if d.open else S.DOOR_CLOSED_COLOR
            pg.draw.rect(surf, color, _apply(d.rect))
