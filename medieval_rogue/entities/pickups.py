from __future__ import annotations
import pygame as pg
from dataclasses import dataclass
from medieval_rogue.entities.player import Player
from medieval_rogue.camera import Camera

@dataclass
class ItemPickup:
    x: float
    y: float
    item_id: str

    alive: bool = True
    w: int = 16
    h: int = 16

    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x - self.w // 2), int(self.y - self.h // 2), self.w, self.h)

    def update(self, dt: float, player: Player) -> None:
        if not self.alive:
            return
        if self.rect().colliderect(player.rect()):
            self.alive = False

    def draw(self, surf: pg.Surface, camera: Camera | None = None) -> None:
        r = self.rect()
        if camera is not None:
            sx, sy = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(sx, sy, r.w, r.h)
        pg.draw.rect(surf, (200, 180, 60), r)
