from __future__ import annotations
import pygame as pg, random
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.entities.player import Player, PlayerStats
from medieval_rogue.entities.enemy_registry import BOSSES
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.enemy_registry import create_boss, spawn_from_pattern, SPAWN_PATTERNS
from medieval_rogue.dungeon.generation import generate_floor
from medieval_rogue.dungeon.room import Room, Direction
from medieval_rogue.items.basic_items import get_item_by_name, ITEMS
from medieval_rogue.ui.hud import draw_hud
from medieval_rogue.ui.minimap import draw_minimap
from assets.sound_manager import load_sounds
from medieval_rogue.camera import Camera
from medieval_rogue.entities.pickups import ItemPickup

class RunScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.camera = Camera()
        self.sounds = load_sounds()
        # create player from chosen class if the character select set it on the app.
        pc = getattr(self.app, "chosen_class", None)
        if pc is not None:
            stats = PlayerStats(
                max_hp = pc.max_hp,
                speed = pc.speed,
                firerate = pc.firerate,
                proj_speed = pc.proj_speed,
                damage = pc.damage,
            )
        else:
            stats = PlayerStats()
        self.player = Player(S.BASE_W//2, S.BASE_H//2, stats=stats)
        self.player.sfx_shot = self.sounds.get("arrow_shot")
        self.projectiles: list[Projectile] = []
        self.e_projectiles: list[Projectile] = []
        self.enemies = []
        self.boss = None
        self.floor = generate_floor(0)
        self.rooms: dict[tuple[int,int], Room] = self.floor.rooms
        self.current_gp = self.floor.start
        self.current_room: Room = self.rooms[self.current_gp]
        self.current_room.visited = True
        for _, r in self._neighbors_of(self.current_gp).items():
            if r: r.discovered = True
        self.floor_i = 0; self.room_i = 0
        self.max_hp = self.player.stats.max_hp
        self.message = ""; self.room_cleared = False
        self.item_pickup: ItemPickup | None = None
        self.score = 10
        self.timescale = 1.0; self.hitstop_timer = 0.0; self.entry_freeze = 0.4; self.time_decay = 0.0
        self.sfx_player_hit = self.sounds["player_hit"]; self.sfx_player_hit.set_volume(0.2)
        self._enter_room(self.current_gp, from_dir=None)

    def _neighbors_of(self, gp):
        gx, gy = gp
        return {"N": self.rooms.get((gx, gy-1)), "S": self.rooms.get((gx, gy+1)), "W": self.rooms.get((gx-1, gy)), "E": self.rooms.get((gx+1, gy))}

    def _enter_room(self, gp, from_dir: Direction | None):
        self.current_gp = gp
        self.current_room = self.rooms[gp]
        self.current_room.visited = True
        nbrs = self._neighbors_of(gp)
        for _, r in nbrs.items():
            if r: r.discovered = True
        self.current_room.compute_doors(nbrs)

        self.walls = self.current_room.wall_rects()
        self.enemies.clear()
        self.projectiles.clear()
        self.e_projectiles.clear()
        self.boss = None
        self.item_available = None

        if self.current_room.kind == "combat":
            self._spawn_combat_wave()
        elif self.current_room.kind == "item":
            self._spawn_item()
        elif self.current_room.kind == "boss":
            self._spawn_boss_encounter()

        self._place_player_on_entry(from_dir)
        self.camera.x = float(self.current_room.world_rect.centerx - self.camera.w // 2)
        self.camera.y = float(self.current_room.world_rect.centery - self.camera.h // 2)
        self.camera.clamp_to_room(self.current_room.world_rect.w, self.current_room.world_rect.h)

    def _place_player_on_entry(self, from_dir: Direction | None) -> None:
        r = self.current_room.world_rect
        if from_dir == "N": self.player.x, self.player.y = r.centerx, r.top + 80
        elif from_dir == "S": self.player.x, self.player.y = r.centerx, r.bottom - 80
        elif from_dir == "W": self.player.x, self.player.y = r.left + 80, r.centery
        elif from_dir == "E": self.player.x, self.player.y = r.right - 80, r.centery
        else: self.player.x, self.player.y = r.centerx, r.centery

    def _spawn_combat_wave(self) -> None:
        rng = random.Random(S.RANDOM_SEED)
        pattern_name = rng.choice(list(SPAWN_PATTERNS.keys()))
        r = self.current_room.world_rect
        spawned = spawn_from_pattern(pattern_name, r)
        self.enemies.extend(spawned)
        self.message = f"Enemies: {len(spawned)}"

    def _spawn_item(self) -> None:
        r = self.current_room.world_rect
        name = random.choice(ITEMS).name
        self.item_pickup = ItemPickup(r.centerx, r.centery, item_id=name)
        self.message = f"Item: {name}"

    def _spawn_boss_encounter(self) -> None:
        r = self.current_room.world_rect
        boss_ids = list(BOSSES.keys())
        boss_id = random.choice(boss_ids)
        self.boss = create_boss(boss_id, r.centerx, r.centery)
        self.message = f"Boss: {boss_id}"

    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            self.next_scene = "menu"

    def update(self, dt: float) -> None:
        if self.entry_freeze > 0:
            self.entry_freeze -= dt
            return      # skip updating while frozen

        room = self.current_room
        walls = room.wall_rects()

        keys = pg.key.get_pressed(); mouse_buttons = pg.mouse.get_pressed(); mouse_pos = pg.mouse.get_pos()
        # Convert to world-space for aiming
        world_mouse = (self.camera.x + mouse_pos[0], self.camera.y + mouse_pos[1])
        win_w, win_h = self.app.window.get_size()
        scale_x = win_w / S.BASE_W
        scale_y = win_h / S.BASE_H
        self.player.update(dt, keys, mouse_buttons, world_mouse, walls, self.projectiles)
        self.camera.follow(self.player.x, self.player.y)
        self.camera.clamp_to_room(S.BASE_W, S.BASE_H)

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
        if (self.current_room.kind in ("combat", "boss") and
            not self.enemies and (not self.boss or self.boss.hp <= 0)):
            if not self.current_room.cleared:
                self.current_room.cleared = True
                self.score += S.SCORE_PER_ROOM
                for d in self.current_room.doors.values():
                    d.open = True

        # Time decay
        self.time_decay += dt
        while self.time_decay >= 1.0:
            self.time_decay -= 1.0
            self.score -= S.SCORE_DECAY_PER_SEC

        # Room advance
        if self.current_room.doors:
            prect = self.player.rect()
            for side, door in self.current_room.doors.items():
                if not door.open:
                    continue
                if prect.colliderect(door.rect):
                    gx, gy = self.current_gp
                    if side == "N": nxt = (gx, gy-1)
                    elif side == "S": nxt = (gx, gy+1)
                    elif side == "W": nxt = (gx-1, gy)
                    else: nxt = (gx+1, gy)
                    if nxt in self.rooms:
                        self._enter_room(nxt, from_dir={"N":"S","S":"N","W":"E","E":"W"}[side])
                        break

        # Camera
        self.camera.follow(self.player.x, self.player.y)
        self.camera.clamp_to_room(self.current_room.world_rect.w, self.current_room.world_rect.h)

        # Player death
        if self.player.hp <= 0:
            self.app.final_score = int(self.score)
            self.next_scene = "gameover"

    def draw(self, surf: pg.Surface) -> None:
        w, h = S.BASE_W, S.BASE_H
        self.current_room.draw(surf, camera=self.camera)
        for p in self.projectiles: p.draw(surf, camera=self.camera)
        for p in self.e_projectiles: p.draw(surf, camera=self.camera)
        for e in self.enemies: e.draw(surf, camera=self.camera)
        self.player.draw(surf, camera=self.camera)
        if self.boss:
            self.boss.draw(surf, camera=self.camera)
            pg.draw.rect(surf, (60,40,40), (20, 28, w - 40, 6))
            hpw = int((w-40) * max(0, self.boss.hp) / self.boss.max_hp)
            pg.draw.rect(surf, (200,80,80), (20, 28, hpw, 6))
        if self.message:
            txt = self.app.font.render(self.message, True, (220,220,220))
            surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, surf.get_height()-48))
        draw_hud(surf, self.app.font, self.player.hp, self.max_hp, int(self.score), self.floor_i, self.room_i)
        draw_minimap(surf, self.rooms, self.current_gp)
