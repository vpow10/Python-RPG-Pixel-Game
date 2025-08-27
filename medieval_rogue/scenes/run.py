from __future__ import annotations
import pygame as pg, random
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.entities.player import Player, PlayerStats
from medieval_rogue.entities.boss import BOSSES
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
        self.player = Player(S.BASE_W//2, S.BASE_H//2, stats=PlayerStats())
        self.player.sfx_shot = self.sounds.get("arrow_shot")
        self.projectiles: list[Projectile] = []
        self.e_projectiles: list[Projectile] = []
        self.enemies = []
        self.boss = None
        self.floor = generate_floor(0)
        self.rooms: dict[tuple[int,int], Room] = self.floor.rooms
        self.current_gp = self.floor.start
        self.current_room: Room = self.rooms[self.current_gp]
        self.floor_i = 0; self.room_i = 0
        self.max_hp = self.player.stats.max_hp
        self.message = ""; self.room_cleared = False
        self.item_pickup: ItemPickup | None = None
        self.score = 0
        self.timescale = 1.0; self.hitstop_timer = 0.0; self.entry_freeze = 0.4
        self.sfx_player_hit = self.sounds["player_hit"]; self.sfx_player_hit.set_volume(0.2)
        self._enter_room(self.current_gp, from_dir=None)

    def _neighbors_of(self, gp):
        gx, gy = gp
        return {"N": self.rooms.get((gx, gy-1)), "S": self.rooms.get((gx, gy+1)), "W": self.rooms.get((gx-1, gy)), "E": self.rooms.get((gx+1, gy))}

    def _enter_room(self, gp, from_dir: Direction | None):
        self.current_gp = gp
        self.current_room = self.rooms[gp]
        self.current_room.visited = True
        self.current_room.compute_doors(self._neighbors_of(gp))
        self.enemies.clear(); self.e_projectiles.clear(); self.projectiles.clear()
        self.room_cleared = False; self.item_pickup = None; self.boss = None
        if self.current_room.kind == "combat": self._spawn_combat_wave()
        elif self.current_room.kind == "item": self._spawn_item()
        elif self.current_room.kind == "boss": self._spawn_boss_encounter()
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
        name = random.choice(BOSSES)
        self.boss = create_boss(name, r.centerx, r.centery)
        self.message = "Boss!"

    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
            self.next_scene = "menu"

    def update(self, dt: float) -> None:
        if self.hitstop_timer > 0:
            self.hitstop_timer -= dt
            if self.hitstop_timer <= 0: self.timescale = 1.0
        dt *= self.timescale

        keys = pg.key.get_pressed(); mouse_buttons = pg.mouse.get_pressed(); mouse_pos = pg.mouse.get_pos()
        walls = self.current_room.wall_rects()
        if self.entry_freeze > 0: self.entry_freeze -= dt
        else: self.player.update(dt, keys, mouse_buttons, mouse_pos, walls, self.projectiles)

        self.camera.follow(self.player.x, self.player.y)
        self.camera.clamp_to_room(self.current_room.world_rect.w, self.current_room.world_rect.h)

        for p in self.projectiles: p.update(dt, walls)
        for p in self.e_projectiles: p.update(dt, walls)
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.e_projectiles = [p for p in self.e_projectiles if p.alive]

        for e in self.enemies: e.update(dt, self.player.center(), walls, self.e_projectiles)
        self.enemies = [e for e in self.enemies if e.alive]

        for p in self.projectiles:
            if not p.alive: continue
            for e in self.enemies:
                if e.alive and p.rect().colliderect(e.rect()):
                    e.hp -= p.damage; p.alive = False
                    if e.hp <= 0: e.alive = False; self.score += 10

        for p in self.e_projectiles:
            if p.alive and p.rect().colliderect(self.player.rect()):
                if self.player.take_damage(1):
                    self.sfx_player_hit.play(); p.alive = False
                    self.timescale = 0.05; self.hitstop_timer = 0.03

        for e in self.enemies:
            if e.alive and self.player.rect().colliderect(e.rect()):
                if self.player.take_damage(e.touch_damage):
                    self.sfx_player_hit.play(); self.timescale = 0.05; self.hitstop_timer = 0.03

        if self.boss:
            if self.boss.alive:
                self.boss.update(dt, self.player.center(), walls, self.e_projectiles)
                if self.player.rect().colliderect(self.boss.rect()):
                    if self.player.take_damage(1):
                        self.sfx_player_hit.play(); self.timescale = 0.05; self.hitstop_timer = 0.03
            else:
                self.current_room.cleared = True; self.message = "Boss defeated!"
        else:
            if not self.enemies and (self.current_room.kind != "item" or (self.item_pickup and not self.item_pickup.alive)):
                self.current_room.cleared = True; self.message = "Cleared!"

        self.current_room.compute_doors(self._neighbors_of(self.current_gp))

        if self.current_room.kind == "item" and self.item_pickup and self.item_pickup.alive:
            self.item_pickup.update(dt, self.player)
            if not self.item_pickup.alive:
                it = get_item_by_name(self.item_pickup.item_id)
                if it: self.player.apply_item(it)

        if self.player.hp <= 0:
            self.next_scene = "gameover"

    def draw(self, surf: pg.Surface) -> None:
        w, h = S.BASE_W, S.BASE_H
        self.current_room.draw(surf)
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
