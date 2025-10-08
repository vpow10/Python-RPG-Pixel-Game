from __future__ import annotations
import pygame as pg
from dataclasses import dataclass
from medieval_rogue import settings as S


@dataclass
class Camera:
    w: int = S.BASE_W; h: int = S.BASE_H
    x: float = 0.0; y: float = 0.0
    shake_x: float = 0.0; shake_y: float = 0.0

    def follow(self, target_x: float, target_y: float, lerp: float = 0.18) -> None:
        target_cam_x = target_x - self.w / 2
        target_cam_y = target_y - self.h / 2
        self.x += (target_cam_x - self.x) * lerp
        self.y += (target_cam_y - self.y) * lerp

    def clamp_to_room(self, room_rect: pg.Rect) -> None:
        inset = int(S.ROOM_INSET)
        wall = int(S.WALL_THICKNESS)
        band = max(8, min(int(S.VIEW_GUTTER), inset + wall - 8))

        interior = room_rect.inflate(-2*inset, -2*inset)
        min_x = max(room_rect.left,  interior.left - band)
        min_y = max(room_rect.top,   interior.top  - band)
        max_x = min(room_rect.right - self.w, interior.right - self.w + band)
        max_y = min(room_rect.bottom - self.h, interior.bottom - self.h + band)

        # Handle tiny rooms
        if max_x < min_x: max_x = min_x
        if max_y < min_y: max_y = min_y

        if self.x < min_x: self.x = float(min_x)
        if self.y < min_y: self.y = float(min_y)
        if self.x > max_x: self.x = float(max_x)
        if self.y > max_y: self.y = float(max_y)

    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        sx = int(round(wx - self.x + self.shake_x))
        sy = int(round(wy - self.y + self.shake_y))
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        return float(sx + self.x - self.shake_x), float(sy + self.y - self.shake_y)

    def apply_rect(self, rect: pg.Rect) -> pg.Rect:
        sx, sy = self.world_to_screen(rect.x, rect.y)
        return pg.Rect(int(sx), int(sy), int(rect.w), int(rect.h))

    def apply_pos(self, x: float, y: float) -> tuple[int, int]:
        return self.world_to_screen(x, y)

    def center_on(self, x: float, y: float):
        self.x = int(x - self.w // 2)
        self.y = int(y - self.h // 2)