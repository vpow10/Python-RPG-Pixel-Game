from __future__ import annotations
import pygame as pg
from dataclasses import dataclass
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera


@dataclass
class Projectile:
    x: float; y: float; vx: float; vy: float
    radius: int; damage: int; friendly: bool
    alive: bool = True

    def rect(self) -> pg.Rect:
        r = self.radius
        return pg.Rect(int(self.x - r), int(self.y - r), 2*r, 2*r)

    def update(self, dt: float, walls: list[pg.Rect]) -> None:
        if not self.alive: return
        dx = self.vx * dt
        dy = self.vy * dt
        nx, ny, collided = move_and_collide(self.x, self.y, self.radius*2, self.radius*2, dx, dy, walls, ox=-self.radius, oy=-self.radius, stop_on_collision=True)
        if collided:
            self.alive = False
            return
        self.x, self.y = nx, ny

    def draw(self, surf: pg.Surface, camera: Camera=None) -> None:
        color = (240,220,120) if self.friendly else (220,90,90)
        pos = (int(self.x), int(self.y))
        if camera is not None:
            pos = camera.world_to_screen(self.x, self.y)
        pg.draw.circle(surf, color, pos, self.radius)