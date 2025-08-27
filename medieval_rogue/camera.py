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
        min_x = room_rect.left
        min_y = room_rect.top
        max_x = max(min_x, room_rect.right - self.w)
        max_y = max(min_y, room_rect.bottom - self.h)

        if self.x < min_x:
            self.x = float(min_x)
        if self.y < min_y:
            self.y = float(min_y)
        if self.x > max_x:
            self.x = float(max_x)
        if self.y > max_y:
            self.y = float(max_y)

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