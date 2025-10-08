from __future__ import annotations
import pygame as pg, math
from dataclasses import dataclass
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera
from assets.sprite_manager import _load_image


@dataclass
class Projectile:
    x: float; y: float; vx: float; vy: float
    radius: int; damage: int; friendly: bool
    sprite_id: str | None = None
    color: tuple[int,int,int] | None = None
    alive: bool = True
    sprite: pg.Surface | None = None

    def __post_init__(self):
        if self.sprite is None:
            try:
                self.sprite = _load_image(['assets','sprites','projectiles',f'{self.sprite_id}.png'])
            except Exception:
                self.sprite = None

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
        pos = (int(self.x), int(self.y))
        if camera is not None:
            pos = camera.world_to_screen(self.x, self.y)

        if self.sprite:
            ang = -math.degrees(math.atan2(self.vy, self.vx))
            img = pg.transform.rotozoom(self.sprite, ang, 1.0)
            rect = img.get_rect(center=pos)
            surf.blit(img, rect)
        else:
            if self.color:
                color = self.color
            else:
                color = (240,220,120) if self.friendly else (220,90,90)
            pg.draw.circle(surf, color, pos, self.radius)