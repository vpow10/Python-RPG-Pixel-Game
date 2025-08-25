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
        
    def clamp_to_room(self, room_pixel_w: int, room_pixel_h: int) -> None:
        max_x = max(0, room_pixel_w - self.w)
        max_y = max(0, room_pixel_h - self.h)
        if self.x < 0: self.x = 0.0
        if self.y < 0: self.y = 0.0
        if self.x > max_x: self.x = float(max_x)
        if self.y > max_y: self.y = float(max_y)
        
    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        sx = int(round(wx - self.x + self.shake_x))
        sy = int(round(wy - self.y + self.shake_y))
        return sx, sy
    
    def apply_rect(self, rect: pg.Rect) -> pg.Rect:
        return rect.move(-int(round(self.x - self.shake_x)), -int(round(self.y - self.shake_y)))
