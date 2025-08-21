from __future__ import annotations
import pygame as pg
from .. import settings as S
from ..scene_manager import Scene
from ..entities.player import Player
from ..entities.projectile import Projectile


class RunScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        stats = getattr(self.app, "chosen_stats", None) or {}
        self.player = Player(160, 90, **{k:v for k,v in stats.items() if k != "name"})
        self.projectiles: list[Projectile] = []
    
    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            self.next_scene = "menu"
        
    def update(self, dt: float) -> None:
        keys = pg.key.get_pressed()
        mpos = pg.mouse.get_pos()
        scale_x = self.app.window.get_width() // S.BASE_W
        scale_y = self.app.window.get_height() // S.BASE_H
        mpos = (mpos[0] // scale_x, mpos[1] // scale_y)
        mbtn = pg.mouse.get_pressed(3)
        self.player.update(dt, keys, mpos, mbtn, self.projectiles)
        bounds = pg.Rect(0,0,S.BASE_W,S.BASE_H)
        for p in self.projectiles: p.update(dt, bounds)
        self.projectiles = [p for p in self.projectiles if p.alive]
    
    def draw(self, surf: pg.Surface) -> None:
        surf.fill((26,22,32))
        for p in self.projectiles: p.draw(surf)
        self.player.draw(surf)