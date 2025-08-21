from __future__ import annotations
import pygame as pg
from dataclasses import dataclass


@dataclass
class Projectile:
    x: float; y: float; vx: float; vy: float
    radius: int; damage: int; friendly: bool
    alive: bool = True
    
    def rect(self) -> pg.Rect:
        r = self.radius
        return pg.Rect(int(self.x - r), int(self.y - r), 2*r, 2*r)
    
    def update(self, dt: float, bounds: pg.Rect) -> None:
        if not self.alive: return
        self.x += self.vx * dt; self.y += self.vy * dt
        if not bounds.collidepoint(self.x, self.y): self.alive = False
    
    def draw(self, surf: pg.Surface) -> None:
        color = (240,220,120) if self.friendly else (220,90,90)
        pg.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)