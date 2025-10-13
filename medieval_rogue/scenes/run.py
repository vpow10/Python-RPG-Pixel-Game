from __future__ import annotations
import pygame as pg, random, math
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.entities.player import Player, PlayerStats
from medieval_rogue.entities.enemy_registry import BOSSES
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.enemy_registry import create_boss, spawn_from_pattern, SPAWN_PATTERNS, pick_spawn_pattern
from medieval_rogue.dungeon.generation import generate_floor
from medieval_rogue.dungeon.room import Room, Direction
from medieval_rogue.items.basic_items import get_item_by_name, ITEMS
from medieval_rogue.ui.hud import draw_hud
from medieval_rogue.ui.minimap import draw_minimap
from assets.sound_manager import load_sounds
from medieval_rogue.camera import Camera
from medieval_rogue.entities.pickups import ItemPickup
from medieval_rogue.ui.edge_fade import draw_edge_fade
from medieval_rogue.ui.lighting import compute_torches_for_room, update_torches, draw_torches, apply_lighting
from medieval_rogue.save.run_state import save_run_state, load_run_save, clear_run_save, has_run_save, pack_player, pack_rooms
from medieval_rogue.save.profile import record_run_started, record_boss_defeated, record_room_cleared


class RunScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.camera = Camera()
        self.timescale = 1.0; self.hitstop_timer = 0.0; self.entry_freeze = 0.4; self.time_decay = 0.0
        self.pause = False
        self.pause_index = 0  # 0=Resume, 1=Save & Quit

        self.sounds = load_sounds()
        pc = getattr(self.app, "chosen_class", None)
        if pc is not None:
            stats = PlayerStats(
                hp = pc.hp,
                speed = pc.speed,
                firerate = pc.firerate,
                proj_speed = pc.proj_speed,
                damage = pc.damage,
            )
        else:
            stats = PlayerStats()
        self.player = Player(S.BASE_W//2, S.BASE_H//2, stats=stats, cls=pc if pc else "archer")
        self.player.sfx_shot = self.sounds.get("arrow_shot")
        self.app.last_run_class_id = self.player.cls.id

        self.projectiles = []; self.e_projectiles = []; self.enemies = []
        self.boss = None; self.torches = []; self.item_pickup = None

        cont = getattr(app, "continue_data", None)
        if cont:
            self.run_seed = int(cont.get("run_seed", random.randrange(2**31)))
        else:
            self.run_seed = random.randrange(2**31)
            record_run_started()

        self.floor_i = 0
        self.score = 10
        self.boss_history = []
        self.boss_pool = list(BOSSES.keys())

        # build floor with deterministic rng
        floor_rng = random.Random(f"{self.run_seed}-F{self.floor_i}-GEN")
        self.floor = generate_floor(self.floor_i, rng=floor_rng)
        self.rooms = self.floor.rooms
        self.current_gp = self.floor.start
        self.current_room = self.rooms[self.current_gp]
        self.current_room.visited = True
        for _, r in self._neighbors_of(self.current_gp).items():
            if r: r.discovered = True

        self.room_cleared = False
        self.item_picked = False
        self.boss_cleared = False
        self.max_hp = self.player.stats.hp
        self.message = ""

        self.camera.center_on(self.player.x, self.player.y)
        self.camera.clamp_to_room(self.current_room.world_rect)

        if cont:
            self._load_from_save(cont)
            app.continue_data = None
        else:
            self._enter_room(self.current_gp, from_dir=None)
            
        self.sfx_player_hit = self.sounds["player_hit"]; self.sfx_player_hit.set_volume(0.1)
        self.sfx_arrow_shot = self.sounds["arrow_shot"]; self.sfx_arrow_shot.set_volume(0.1)

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
        self.torches = compute_torches_for_room(self.current_room)
        self.enemies.clear(); self.projectiles.clear() ;self.e_projectiles.clear()
        self.boss = None; self.item_available = None
        
        self._place_player_on_entry(from_dir)
        self.camera.center_on(self.player.x, self.player.y)
        self.camera.clamp_to_room(self.current_room.world_rect)
        
        self._checkpoint = {
            "entry_gp": [self.current_gp[0], self.current_gp[1]],
            "player_entry": pack_player(self.player),
        }

        if self.current_room.kind == "combat":
            if not self.current_room.cleared:
                self._spawn_combat_wave()
            else:
                self.message = ""
        elif self.current_room.kind == "item":
            if not self.item_picked:
                self._spawn_item()
                self.item_picked = True
        elif self.current_room.kind == "boss":
            if not self.boss_cleared:
                self._spawn_boss_encounter()
                self.boss_cleared = True

    def _place_player_on_entry(self, from_dir: Direction | None) -> None:
        r = self.current_room.world_rect
        M = 16  # small safety margin so we never clip walls
        safe = pg.Rect(
            r.left   + S.ROOM_INSET + S.WALL_THICKNESS + M,
            r.top    + S.ROOM_INSET + S.WALL_THICKNESS + M,
            r.width  - 2*(S.ROOM_INSET + S.WALL_THICKNESS + M),
            r.height - 2*(S.ROOM_INSET + S.WALL_THICKNESS + M),
        )

        if from_dir == "N":      self.player.x, self.player.y = safe.centerx, safe.top + 40
        elif from_dir == "S":    self.player.x, self.player.y = safe.centerx, safe.bottom - 40
        elif from_dir == "W":    self.player.x, self.player.y = safe.left + 40, safe.centery
        elif from_dir == "E":    self.player.x, self.player.y = safe.right - 40, safe.centery
        else:                    self.player.x, self.player.y = safe.centerx, safe.centery

        self.player.set_position(self.player.x, self.player.y)

    def _find_free_spot(self, preferred: tuple[float, float], walls: list[pg.Rect], w: int = 16, h: int = 16,
                        max_radius: int = 200, step: int = 8) -> tuple[float, float]:
        """
        Find a free spot near `preferred` (world coords) where a w x h rect does not collide with walls
        and stays inside the current room bounds. Returns (x,y). Uses a spiral sample.
        """
        px, py = float(preferred[0]), float(preferred[1])
        room_rect = self.current_room.world_rect

        def collides(x: float, y: float) -> bool:
            r = pg.Rect(int(x - w // 2), int(y - h // 2), w, h)
            # must be inside room (respect border)
            if r.left < room_rect.left + S.BORDER or r.right > room_rect.right - S.BORDER or \
               r.top < room_rect.top + S.BORDER or r.bottom > room_rect.bottom - S.BORDER:
                return True
            for wr in walls:
                if r.colliderect(wr):
                    return True
            return False

        # Try preferred
        if not collides(px, py):
            return px, py

        # Spiral search
        for radius in range(step, max_radius + 1, step):
            # sample 24 angles per radius
            for a_deg in range(0, 360, 15):
                ang = math.radians(a_deg)
                x = px + math.cos(ang) * radius
                y = py + math.sin(ang) * radius
                if not collides(x, y):
                    return float(x), float(y)

        # fallback: nearest room-center clamped inside room
        cx, cy = room_rect.centerx, room_rect.centery
        cx = max(room_rect.left + S.BORDER + w//2, min(cx, room_rect.right - S.BORDER - w//2))
        cy = max(room_rect.top + S.BORDER + h//2, min(cy, room_rect.bottom - S.BORDER - h//2))
        return float(cx), float(cy)

    def _advance_floor(self) -> None:
        self.floor_i += 1
        if self.floor_i >= S.FLOORS:
            self.app.final_score = int(self.score)
            self.next_scene = "victory"
            return
        floor_rng = random.Random(f"{self.run_seed}-F{self.floor_i}-GEN")
        self.floor = generate_floor(self.floor_i, rng=floor_rng)
        self.rooms = self.floor.rooms
        self.current_gp = self.floor.start
        self._enter_room(self.current_gp, from_dir=None)
        self.room_cleared = False
        self.item_picked = False
        self.boss_cleared = False

    def _spawn_combat_wave(self) -> None:
        rng = random.Random(f"{self.run_seed}-F{self.floor_i}-R{self.current_gp[0]}_{self.current_gp[1]}")
        r = self.current_room.world_rect
        name = pick_spawn_pattern(self.current_room.w_cells, self.current_room.h_cells, rng)
        spawned = spawn_from_pattern(
            name, r,
            avoid_pos=(self.player.x, self.player.y),
            avoid_radius=getattr(S, "SAFE_RADIUS", 160)
        )
        self.enemies.extend(spawned)
        self.message = f"Enemies: {len(spawned)}"

    def _spawn_item(self) -> None:
        r = self.current_room.world_rect
        name = random.choice(ITEMS).name
        preferred = (r.centerx, r.centery)
        sx, sy = self._find_free_spot(preferred, self.walls, w=16, h=16)
        self.item_pickup = ItemPickup(sx, sy, item_id=name)
        self.message = f"Item: {name}"
        
    def _next_boss_id(self) -> str:
        forced = getattr(S, "FORCE_BOSS_ID", None)
        if forced in BOSSES.keys() and forced not in self.boss_history:
            self.boss_history.append(forced)
            return forced

        for bid in self.boss_pool:
            if bid not in self.boss_history:
                self.boss_history.append(bid)
                return bid
            
        # fallback 1    
        remaining = [bid for bid in BOSSES.keys() if bid not in self.boss_history]
        if remaining:
            bid = random.choice(remaining)
            self.boss_history.append(bid)
            return bid
        
        # fallback 2 
        return random.choice(list(BOSSES.keys()))

    def _spawn_boss_encounter(self) -> None:
        r = self.current_room.world_rect
        boss_id = self._next_boss_id()
        self.boss = create_boss(boss_id, r.centerx, r.centery)
        
    def _save_and_quit_to_menu(self) -> None:
        world = pack_rooms(self.rooms)
        cx, cy = int(self.player.x), int(self.player.y)
        data = {
            "version": 1,
            "run_seed": int(self.run_seed),
            "floor_i": int(self.floor_i),
            "current_gp": [int(self.current_gp[0]), int(self.current_gp[1])],
            "rooms": world,
            "checkpoint": self._checkpoint,
            "resume": {
                "mid_room": not self.current_room.cleared and self.current_room.kind == "combat",
                "player_pos": [cx, cy],
            },
            "player_entry_class": self._checkpoint["player_entry"]["class_id"],
            "score": int(self.score),
        }
        save_run_state(data)
        self.next_scene = "menu"
        
    def _load_from_save(self, data: dict) -> None:
        self.run_seed = int(data["run_seed"])
        self.floor_i = int(data["floor_i"])
        floor_rng = random.Random(f"{self.run_seed}-F{self.floor_i}-GEN")
        self.floor = generate_floor(self.floor_i, rng=floor_rng)
        self.rooms = self.floor.rooms
        
        for key, flags in data.get("rooms", {}).items():
            gp = tuple(int(x) for x in key.split(","))
            r = self.rooms.get(gp)
            if not r: continue
            r.kind = flags.get("kind", r.kind)
            r.visited = flags.get("visited", False)
            r.discovered = flags.get("discovered", False)
            r.cleared = flags.get("cleared", False)
            
        self.current_gp = tuple(data["current_gp"])
        self.current_room = self.rooms[self.current_gp]
        self.current_room.compute_doors(self._neighbors_of(self.current_gp))
        
        entry = data["checkpoint"]["player_entry"]
        pc = getattr(self.app, "selected_class", None)
        saved_class_id = entry.get("class_id", "archer")
        self.player.hp = int(entry["hp"])
        st = entry["stats"]
        self.player.stats.hp = int(st["hp"])
        self.player.stats.damage = float(st["damage"])
        self.player.stats.speed = float(st["speed"])
        self.player.stats.firerate = float(st["firerate"])
        self.player.stats.proj_speed = float(st["proj_speed"])
        self.player.inventory = list(entry.get("inventory", []))
        
        self._enter_room(self.current_gp, from_dir=None)
        
        resume = data.get("resume", {})
        if not resume.get("mid_room", False):
            px, py = resume.get("player_pos", [self.player.x, self.player.y])
            self.player.set_position(px, py)
            self.camera.center_on(px, py)

    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                self.pause = not self.pause
                return
            if e.key == pg.K_n:
                if self.room_cleared and self.current_room.kind == "boss":
                    self._advance_floor()
        if self.pause:
            if e.type == pg.KEYDOWN:
                if e.key in (pg.K_UP, pg.K_w): self.pause_index = (self.pause_index - 1) % 2
                if e.key in (pg.K_DOWN, pg.K_s): self.pause_index = (self.pause_index + 1) % 2
                if e.key in (pg.K_RETURN, pg.K_SPACE):
                    if self.pause_index == 0:
                        self.pause = False
                    else:
                        self._save_and_quit_to_menu()
            return
        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                self.sfx_arrow_shot.play()

    def update(self, dt: float) -> None:
        if self.pause:
            return
        if self.entry_freeze > 0:
            self.entry_freeze -= dt
            return      # skip updating while frozen

        room = self.current_room
        walls = room.wall_rects()

        keys = pg.key.get_pressed(); mouse_buttons = pg.mouse.get_pressed(); mouse_pos = pg.mouse.get_pos()
        
        # Camera
        self.camera.follow(self.player.x, self.player.y)
        self.camera.clamp_to_room(self.current_room.world_rect)
        
        # Convert to world-space for aiming
        world_mouse = self.camera.screen_to_world(mouse_pos[0], mouse_pos[1])

        # For hitstop
        dt *= self.timescale
        if self.hitstop_timer > 0:
            self.hitstop_timer -= dt
            if self.hitstop_timer <= 0:
                self.timescale = 1.0

        # Torches
        update_torches(self.torches, dt)
        
        # Player
        self.player.update(dt, keys, mouse_buttons, world_mouse, walls, self.projectiles)

        # Player projectiles
        for p in self.projectiles: p.update(dt, walls)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Enemy projectiles
        for e in self.enemies:
            e.update(dt, self.player.center(), walls, self.e_projectiles)
        for p in self.e_projectiles:
            p.update(dt, walls)
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

        # Item
        if self.item_pickup:
            self.item_pickup.update(dt, self.player)
            if not self.item_pickup.alive:
                item_obj = get_item_by_name(self.item_pickup.item_id)
                if item_obj is not None:
                    self.player.apply_item(item_obj)
                    self.message = f"{item_obj.name}, {item_obj.desc}"
                self.item_pickup = None

        # Boss
        if self.boss:
            self.boss.update(dt, self.player.center(), walls, self.e_projectiles)
            if self.boss.rect().colliderect(self.player.rect()):
                if self.player.take_damage(self.boss.touch_damage):
                    self.sfx_player_hit.play()
                    self.timescale = 0.05; self.hitstop_timer = 0.02

        for p in self.projectiles:
            if self.boss and self.boss.alive and p.rect().colliderect(self.boss.rect()):
                self.boss.hp -= p.damage
                p.alive = False
                if self.boss.hp <= 0:
                    self.boss = None
                    self.score += S.SCORE_PER_BOSS
                    record_boss_defeated()
                    self.room_cleared = True
                    if self.floor_i >= S.FLOORS - 1:
                        self.app.final_score = int(self.score)
                        self.next_scene = "victory"
                    self.message = "Boss defeated!"
                    try:
                        name = random.choice(ITEMS).name
                        preferred = (self.current_room.world_rect.centerx, self.current_room.world_rect.centery)
                        sx, sy = self._find_free_spot(preferred, self.walls, w=16, h=16)
                        self.item_pickup = ItemPickup(sx, sy, item_id=name)
                    except Exception:
                        # fallback: center
                        r = self.current_room.world_rect
                        self.item_pickup = ItemPickup(r.centerx, r.centery, item_id=random.choice(ITEMS).name)

        # Room clearance
        if (self.current_room.kind in ("combat", "boss") and
            not self.enemies and (not self.boss or self.boss.hp <= 0)):
            if not self.current_room.cleared:
                self.current_room.cleared = True
                record_room_cleared()
                self.score += S.SCORE_PER_ROOM
                self.message = "Room cleared!"
                for d in self.current_room.doors.values():
                    d.open = True
                self.walls = self.current_room.wall_rects()

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

        # Player death
        if self.player.hp <= 0:
            self.app.final_score = int(self.score)
            self.next_scene = "gameover"

    def draw(self, surf: pg.Surface) -> None:
        w, h = S.BASE_W, S.BASE_H
        self.current_room.draw(surf, camera=self.camera)
        draw_torches(surf, self.camera, self.torches)
        for p in self.projectiles: p.draw(surf, camera=self.camera)
        for p in self.e_projectiles: p.draw(surf, camera=self.camera)
        for e in self.enemies: e.draw(surf, camera=self.camera)
        self.player.draw(surf, camera=self.camera)
        if self.item_pickup and self.item_pickup.alive:
            self.item_pickup.draw(surf, camera=self.camera)
        if self.boss:
            self.boss.draw(surf, camera=self.camera)
            pg.draw.rect(surf, (60,40,40), (100, 100, w - 240, 6))
            hpw = int((w-240) * max(0, self.boss.hp) / self.boss.max_hp)
            pg.draw.rect(surf, (200,80,80), (100, 100, hpw, 6))
            txt = self.app.font.render(f"{self.boss.name}", True, S.RED)
            surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, 48))
        if self.current_room.kind == "boss" and self.room_cleared and not self.boss:
            hint = self.app.font.render("Press N to advance to next floor", True, (230,230,230))
            surf.blit(hint, (surf.get_width()//2 - hint.get_width()//2, surf.get_height()-96))
        if self.message:
            txt = self.app.font.render(self.message, True, (220,220,220))
            surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, surf.get_height()-48))
        apply_lighting(surf, self.camera, self.torches)
        draw_edge_fade(surf, self.camera, self.current_room.world_rect)
        draw_hud(surf, self.app.font, self.player.hp, self.player.stats.hp, int(self.score), self.floor_i)
        draw_minimap(surf, self.rooms, self.current_gp)
        self.camera.follow(self.player.x, self.player.y)
        
        if self.pause:
            w, h = surf.get_size()
            pg.draw.rect(surf, (0,0,0,180), (0,0,w,h))
            panel = pg.Surface((420, 220), pg.SRCALPHA)
            panel.fill((20,24,32,230))
            x = w//2 - panel.get_width()//2
            y = h//2 - panel.get_height()//2
            surf.blit(panel, (x,y))
            title = self.app.font.render("Paused", True, (230,230,230))
            surf.blit(title, (w//2 - title.get_width()//2, y + 24))
            opts = ["Resume", "Save & Quit to Menu"]
            for i, label in enumerate(opts):
                sel = (i == self.pause_index)
                col = (255,255,255) if sel else (160,160,160)
                row = self.app.font_small.render(label, True, col)
                surf.blit(row, (w//2 - row.get_width()//2, y + 90 + 44 * i))
            seed = self.app.font_small.render(f"Seed: {self.run_seed}", True, (210,210,210))
            surf.blit(seed, (w//2 - seed.get_width()//2, surf.get_height() - 96))