from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.entities.player import Player
from medieval_rogue.entities.boss import Boss, BOSSES
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.enemy import Enemy, ENEMY_TYPES
from medieval_rogue.dungeon.generation import generate_floor, spawn_enemies_for_room
from medieval_rogue.dungeon.room import Room
from medieval_rogue.items.basic_items import Item, ITEMS
from medieval_rogue.ui.hud import draw_hud
from assets.sound_manager import load_sounds


class RunScene(Scene):
    def __init__(self, app) -> None:
        pg.init()
        pg.mixer.init()
        self.sounds = load_sounds()
        super().__init__(app)
        stats = getattr(self.app, "chosen_stats", None) or {}
        self.player = Player(160, 90, **{k:v for k,v in stats.items() if k != "name"})
        self.projectiles: list[Projectile] = []
        self.enemies: list[Enemy] = []
        self.e_projectiles: list[Projectile] = []
        self.floor_i: int = 0
        self.room_i: int = 0
        self.rooms: list[Room] = generate_floor(self.floor_i).rooms
        self.room: Room = self.rooms[self.room_i]
        self.enemies.clear(); self.e_projectiles.clear()
        self._enter_room(self.room)
        self.boss: Boss = None
        self.max_hp: int = self.player.hp * 2
        self.message: str = ""
        self.room_cleared: bool = False
        self.item_available: Item | None = None
        self.score: int = 10
        self.time_decay: float = 0.0
        self.timescale: float = 1.0
        self.hitstop_timer: float = 0.0
        self.entry_freeze: float = 0.5
        self.sfx_player_hit = self.sounds["player_hit"]
        self.sfx_player_hit.set_volume(0.2)
        # self.sfx_kill = pg.mixer.Sound("assets/sfx/kill.wav")     # in future

    def _enter_room(self, room: Room):
        self.room = room

        import random
        self.enemies.clear()
        self.e_projectiles.clear()
        self.projectiles.clear()
        self.item_available = None
        self.boss = None

        self.room_cleared = False
        self.message = ""

        if room.type == "combat":
            rng = random.Random()
            for cls, (x, y) in spawn_enemies_for_room(rng, self.player):
                self.enemies.append(cls(x, y))
        elif room.type == "item":
            self.item_available = random.choice(ITEMS)
            self.message = f"Item: {self.item_available.name} - {self.item_available.desc} (press E)"
        elif room.type == "boss":
            BossCls = BOSSES[min(self.floor_i, len(BOSSES)-1)]
            self.boss = BossCls(160, 90)
            self.message = f"Boss: {self.boss.name}"

        self.entry_freeze = 0.5

    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            self.next_scene = "menu"
        if e.type == pg.KEYDOWN and e.key == pg.K_e and self.item_available:
            self.item_available.apply(self.player)
            self.max_hp = max(self.max_hp, self.player.hp)
            self.item_available = None
            self.room_cleared = True
            self.message = "Item taken! Press Space for next room."
        if e.type == pg.KEYDOWN and e.key == pg.K_SPACE and self.room_cleared:
            self.room_i += 1
            if self.room_i >= len(self.rooms):
                pass
            else:
                self._enter_room(self.rooms[self.room_i])

    def update(self, dt: float) -> None:
        if self.entry_freeze > 0:
            self.entry_freeze -= dt
            return      # skip updating while frozen

        room = self.room
        walls = room.walls()

        keys = pg.key.get_pressed()
        mx, my = pg.mouse.get_pos()
        win_w, win_h = self.app.window.get_size()
        scale_x = win_w / S.BASE_W
        scale_y = win_h / S.BASE_H
        mpos = (mx / scale_x, my / scale_y)
        mbtn = pg.mouse.get_pressed(3)
        self.player.update(dt, keys, mpos, mbtn, self.projectiles, walls)

        # For hitstop
        dt *= self.timescale
        if self.hitstop_timer > 0:
            self.hitstop_timer -= dt
            if self.hitstop_timer <= 0:
                self.timescale = 1.0

        # Player projectiles
        for p in self.projectiles: p.update(dt, walls)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Enemy projectiles
        for e in self.enemies:
            e.update(dt, self.player.center(), self.e_projectiles, walls)
        for p in self.e_projectiles: p.update(dt, walls)
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
                    self.sfx_player_hit.play()
                    p.alive = False
                    self.timescale = 0.05; self.hitstop_timer = 0.02

        # Enemy touch vs player
        for e in self.enemies:
            if e.alive and self.player.rect().colliderect(e.rect()):
                if self.player.take_damage(e.touch_damage):
                    self.sfx_player_hit.play()
                    self.timescale = 0.05; self.hitstop_timer = 0.02

        # Boss
        if self.boss:
            self.boss.update(dt, self.player.center(), self.e_projectiles, self.enemies, walls)
            if self.boss.rect().colliderect(self.player.rect()):
                if self.player.take_damage(self.boss.touch_damage):
                    self.sfx_player_hit.play()
                    self.timescale = 0.05; self.hitstop_timer = 0.02

        for p in self.projectiles:
            if self.boss and self.boss.alive and p.rect().colliderect(self.boss.rect()):
                self.boss.hp -= p.damage; p.alive = False
                if self.boss.hp <= 0:
                    self.boss = None
                    self.score += S.SCORE_PER_BOSS
                    self.room_cleared = True
                    self.message = "Boss defeated! Press Space for next room"

        # Room clearance
        if not self.boss and not self.enemies and not self.item_available and not self.room_cleared:
            self.room_cleared = True
            self.score += S.SCORE_PER_ROOM
            self.message = "Room cleared! Press Space for next room."

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
            hpw = int(280 * max(0, self.boss.hp) / self.boss.max_hp)
            pg.draw.rect(surf, (200,80,80), (20, 28, hpw, 6))
        # HUD
        draw_hud(surf, self.app.font, self.player.hp, self.max_hp, int(self.score), self.floor_i, self.room_i)

