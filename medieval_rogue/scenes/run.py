from __future__ import annotations
import pygame as pg
from .. import settings as S
from ..scene_manager import Scene
from ..entities.player import Player
from ..entities.projectile import Projectile
from ..entities.enemy import Enemy, ENEMY_TYPES


class RunScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        stats = getattr(self.app, "chosen_stats", None) or {}
        self.player = Player(160, 90, **{k:v for k,v in stats.items() if k != "name"})
        self.projectiles: list[Projectile] = []
        self.enemies: list[Enemy] = []
        self.e_projectiles: list[Projectile] = []
        self.enemies.append(ENEMY_TYPES[0](240, 90))    # temporary spawn to test
    
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
        
        # Player projectiles
        for p in self.projectiles: p.update(dt, bounds)
        self.projectiles = [p for p in self.projectiles if p.alive]
        
        # Enemy projectiles
        for e in self.enemies:
            e.update(dt, self.player.center(), self.e_projectiles)
        for p in self.e_projectiles: p.update(dt, bounds)
        self.e_projectiles = [p for p in self.e_projectiles if p.alive]
        
        # Projectile vs enemy
        for p in self.projectiles:
            if not p.alive: continue
            for e in self.enemies:
                if e.alive and p.rect().colliderect(e.rect()):
                    e.hp -= p.damage; p.alive = False
                    print("Enemy hp:", e.hp)
        self.enemies = [e for e in self.enemies if e.alive]
        
        # Enemy touch vs player
        for e in self.enemies:
            if self.player.rect().colliderect(e.rect()):
                self.player.hp -= e.touch_damage
                print("Player hp:", self.player.hp)
                
    
    def draw(self, surf: pg.Surface) -> None:
        surf.fill((26,22,32))
        for p in self.projectiles: p.draw(surf)
        self.player.draw(surf)
        for e in self.enemies: e.draw(surf)
            