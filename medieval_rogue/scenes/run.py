from __future__ import annotations
import pygame as pg
from .. import settings as S
from ..scene_manager import Scene
from ..entities.player import Player
from ..entities.projectile import Projectile
from ..entities.enemy import Enemy, ENEMY_TYPES
from ..dungeon.generation import generate_floor, spawn_enemies_for_room
from ..dungeon.room import Room
from ..items.basic_items import Item, ITEMS


class RunScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        stats = getattr(self.app, "chosen_stats", None) or {}
        self.player = Player(160, 90, **{k:v for k,v in stats.items() if k != "name"})
        self.projectiles: list[Projectile] = []
        self.enemies: list[Enemy] = []
        self.e_projectiles: list[Projectile] = []
        self.floor_i = 0
        self.room_i = 0
        self.rooms: list[Room] = generate_floor(self.floor_i).rooms
        self.enemies.clear(); self.e_projectiles.clear()
        self._enter_room(self.rooms[self.room_i])
        self.boss = None
        self.max_hp = self.player.hp * 2
        self.message = ""
        self.room_cleared = False
        self.item_available: Item | None = None
        
    def _enter_room(self, room: Room):
        import random
        self.enemies.clear(); self.e_projectiles.clear(); self.item_available = None; self.boss = None
        if room.type == "combat":
            rng = random.Random()
            for cls, (x,y) in spawn_enemies_for_room(rng):
                self.enemies.append(cls(x,y))
        elif room.type == "item":
            self.item_available = random.choice(ITEMS)
            self.message = f"Item: {self.item_available.name} - {self.item_available.desc} (press E)"
        elif room.type == "boss":
            pass
    
    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            self.next_scene = "menu"
        if e.type == pg.KEYDOWN and e.key == pg.K_e and self.item_available:
            self.item_available.apply(self.player)
            self.max_hp = max(self.max_hp, self.player.hp)
            self.item_available = None
            self.room_cleared = True
            self.message = "Item taken! Press N for next room."
        if e.type == pg.KEYDOWN and e.key == pg.K_n and self.room_cleared:
            self.room_i += 1
            if self.room_i >= len(self.rooms):
                # next floor or win 
                pass
            else:
                self._enter_room(self.rooms[self.room_i])
        
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
        self.rooms[self.room_i].draw(surf)
        for p in self.projectiles: p.draw(surf)
        self.player.draw(surf)
        for e in self.enemies: e.draw(surf)
        if self.message:
            txt = self.app.font.render(self.message, True, (220,220,220))
            surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, surf.get_height()-16))
            