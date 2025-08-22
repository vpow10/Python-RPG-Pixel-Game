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
from ..entities.boss import BOSSES
from ..ui.hud import draw_hud


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
        self.score = 10
        self.time_decay = 0.0
        self.timescale = 1.0
        self.hitstop_timer = 0.0
        # self.sfx_hit = pg.mixer.Sound("assets/sfx/hit.wav")       # in future
        # self.sfx_kill = pg.mixer.Sound("assets/sfx/kill.wav")     # in future
        
    def _enter_room(self, room: Room):
        import random
        self.enemies.clear(); self.e_projectiles.clear(); self.item_available = None; self.boss = None
        self.room_cleared = False; self.message = ""
        if room.type == "combat":
            rng = random.Random()
            for cls, (x,y) in spawn_enemies_for_room(rng, self.player):
                self.enemies.append(cls(x,y))
        elif room.type == "item":
            self.item_available = random.choice(ITEMS)
            self.message = f"Item: {self.item_available.name} - {self.item_available.desc} (press E)"
        elif room.type == "boss":
            BossCls = BOSSES[min(self.floor_i, len(BOSSES)-1)]
            self.boss = BossCls(160, 90)
            self.message = f"Boss: {self.boss.name}"
    
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
        
        # For hitstop 
        dt *= self.timescale
        if self.hitstop_timer > 0:
            self.hitstop_timer -= dt
            if self.hitstop_timer <= 0:
                self.timescale = 1.0
        
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
                    # self.sfx_hit.play()
                    if e.hp <= 0:
                        e.alive = False
                        self.score += S.SCORE_PER_ENEMY
                        # self.sfx_kill.play()
        self.enemies = [e for e in self.enemies if e.alive]
        
        # Enemy projectile vs player
        for p in self.e_projectiles:
            if not p.alive: continue
            if p.rect().colliderect(self.player.rect()):
                if self.player.take_damage(1):
                    # self.sfx_hit.play()
                    p.alive = False
                    self.timescale = 0.05; self.hitstop_timer = 0.02
                
        # Enemy touch vs player
        for e in self.enemies:
            if e.alive and self.player.rect().colliderect(e.rect()):
                if self.player.take_damage(e.touch_damage):
                    # self.sfx_hit.play()
                    self.timescale = 0.05; self.hitstop_timer = 0.02
            
        # Boss 
        if self.boss:
            self.boss.update(dt, self.player.center(), self.e_projectiles, self.enemies)
            if self.boss.rect().colliderect(self.player.rect()):
                if self.player.take_damage(self.boss.touch_damage):
                    # self.sfx_hit.play()
                    self.timescale = 0.05; self.hitstop_timer = 0.02

        for p in self.projectiles:
            if self.boss and self.boss.alive and p.rect().colliderect(self.boss.rect()):
                self.boss.hp -= p.damage; p.alive = False
                if self.boss.hp <= 0:
                    self.boss = None
                    self.score += S.SCORE_PER_BOSS
                    self.room_cleared = True
                    self.message = "Boss defeated! Press N..."
        
        # Room clearance
        if not self.boss and not self.enemies and not self.item_available and not self.room_cleared:
            self.room_cleared = True
            self.score += S.SCORE_PER_ROOM
            self.message = "Room cleared! Press N for next room."
            
        # Time decay
        self.time_decay += dt
        while self.time_decay >= 1.0:
            self.time_decay -= 1.0
            self.score -= S.SCORE_DECAY_PER_SEC

        # Room advance (N): if at end of floor
        if self.room_i >= len(self.rooms):
            if self.floor_i + 1 >= S.FLOORS:
                self.app.final_score = int(self.score)
                self.next_scene = "gameover"
            else:
                self.floor_i += 1
                self.rooms = generate_floor(self.floor_i).rooms
                self.room_i = 0
                self._enter_room(self.rooms[self.room_i])
        
        # Player death
        if self.player.hp <= 0:
            self.app.final_score = int(self.score)
            self.next_scene = "gameover"
    
    def draw(self, surf: pg.Surface) -> None:
        surf.fill((26,22,32))
        self.rooms[self.room_i].draw(surf)
        for p in self.projectiles: p.draw(surf)
        for p in self.e_projectiles: p.draw(surf)
        self.player.draw(surf)
        for e in self.enemies: e.draw(surf)
        if self.message:
            txt = self.app.font.render(self.message, True, (220,220,220))
            surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, surf.get_height()-16))
        # Boss
        if self.boss:
            self.boss.draw(surf)
            pg.draw.rect(surf, (60,40,40), (20, 28, 280, 6))
            hpw = int(280 * max(0, self.boss.hp) / 42)
            pg.draw.rect(surf, (200,80,80), (20, 28, hpw, 6))
        # HUD
        draw_hud(surf, self.app.font, self.player.hp, self.max_hp, int(self.score), self.floor_i, self.room_i)

