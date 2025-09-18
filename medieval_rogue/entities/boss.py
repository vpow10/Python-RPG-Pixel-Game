from __future__ import annotations
import pygame as pg, random, math
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera
from medieval_rogue.entities.enemy import Enemy
from medieval_rogue.entities.enemy_registry import register_boss
from assets.sprite_manager import AnimatedSprite, load_strip


@register_boss("the_skull")
class TheSkull(Enemy):     # bouncing + 5-way volley
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=40, speed=360.0, sprite_id="the_skull")
        self.is_boss = True
        self.max_hp = self.hp
        self.vx = 180.0
        self.vy = 135.0
        self.name = "The Skull"

        FRAME_W, FRAME_H = 96, 96
        frames = load_strip(['assets','sprites','bosses','the_skull.png'], FRAME_W, FRAME_H)

        self.sprite = AnimatedSprite(frames, fps=4, loop=True, anchor='center')  

    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        if self.sprite:
            self.sprite.draw(surf, self.x, self.y, camera=camera)
        else:
            r = self.rect()
            if camera is not None:
                sx, sy = camera.world_to_screen(r.x, r.y)
                r = pg.Rect(sx, sy, r.w, r.h)
            pg.draw.rect(surf, (50,220,150), r)

    def update(self, dt, player_pos, walls, projectiles):
        # --- Movement (bounce) ---
        dx = self.vx * dt
        dy = self.vy * dt
        nx, ny, _ = move_and_collide(
            self.x, self.y, 20, 20, dx, dy,
            walls, ox=-10, oy=-10, stop_on_collision=False
        )
        if nx != self.x + dx:
            self.vx *= -1
        if ny != self.y + dy:
            self.vy *= -1
        self.x, self.y = nx, ny

        # --- Animation update ---
        if self.sprite:
            prev_frame = self.sprite.idx
            self.sprite.update(dt)
            new_frame = self.sprite.idx

            if new_frame == 2 and prev_frame != 2:
                self._fire_volley(projectiles)

    def _fire_volley(self, projectiles):
        for ang in (0, 72, 144, 216, 288):
            rad = math.radians(ang)
            projectiles.append(Projectile(
                self.x, self.y,
                math.cos(rad) * 130, math.sin(rad) * 130,
                6, 1, False, sprite_id=None
            ))

@register_boss("warlock")
class Warlock(Enemy):    # bullet rings + 3-shot sync
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=40, speed=0.0, sprite_id="warlock")
        self.t = 0.0
        self.is_boss = True
        self.max_hp = self.hp
        self.spawn_x = float(x)
        self.spawn_y = float(y)
        self.name = "Warlock"

        FRAME_W, FRAME_H = 96, 96
        frames = load_strip(['assets','sprites','bosses','warlock.png'], FRAME_W, FRAME_H)
        self.sprite = AnimatedSprite(frames, fps=4, loop=True, anchor='center')

    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        if self.sprite:
            self.sprite.draw(surf, self.x, self.y, camera=camera)
        else:
            r = self.rect()
            if camera is not None:
                sx, sy = camera.world_to_screen(r.x, r.y)
                r = pg.Rect(sx, sy, r.w, r.h)
            pg.draw.rect(surf, (180,100,220), r)

    def update(self, dt, player_pos, walls, projectiles):
        # --- return to spawn position ---
        dx = (self.spawn_x - self.x) * 0.6 * dt
        dy = (self.spawn_y - self.y) * 0.6 * dt
        nx, ny, _ = move_and_collide(self.x, self.y, 32, 32, dx, dy, walls,
                                     ox=-16, oy=-16, stop_on_collision=False)
        self.x, self.y = nx, ny

        # --- bullet ring timer ---
        self.t += dt
        if self.t >= 0.8:
            self.t = 0.0
            base = random.random() * math.tau
            for i in range(10):
                a = base + (i/10.0)*math.tau
                projectiles.append(Projectile(
                    self.x, self.y,
                    math.cos(a)*150, math.sin(a)*150,
                    6, 1, False, sprite_id="fireball"
                ))

        # --- animation update ---
        if self.sprite:
            prev_frame = self.sprite.idx
            self.sprite.update(dt)
            new_frame = self.sprite.idx

            if new_frame == 2 and prev_frame != 2:
                vec = player_pos - self.center()
                if vec.length_squared() > 0:
                    dirv = vec.normalize()
                    for spread in (-0.22, 0.0, 0.22):
                        v = dirv.rotate_rad(spread)
                        projectiles.append(Projectile(
                            self.x, self.y,
                            v.x*220.0, v.y*220.0,
                            6, 1, False, sprite_id="fireball"
                        ))

@register_boss("knight_captain")
class KnightCaptain(Enemy):      # telegraphed dash + lance projectiles while dashing
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=50, speed=0.0)
        self.is_boss = True
        self.max_hp = self.hp
        self.state = "charge"
        self.cd = 0.8
        self.vx = self.vy = 0.0
        self.dash_emit_cd = 0.12

    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (200,180,80) if self.state=="charge" else (220,140,60), r)

    def update(self, dt, player_pos, walls, projectiles):
        if self.state == "charge":
            self.cd -= dt
            if self.cd < 0:
                d = (player_pos - self.center())
                if d.length_squared() > 0:
                    d = d.normalize()
                    self.vx, self.vy = d.x*360, d.y*360
                    self.cd = 0.6
                    self.state = "dash"
                    self.dash_emit_cd = 0.08  # start a short burst as the dash begins
        else:
            dx = self.vx * dt
            dy = self.vy * dt
            nx, ny, collided = move_and_collide(self.x, self.y, 32, 32, dx, dy, walls, ox=-16, oy=-16, stop_on_collision=False)
            self.x, self.y = nx, ny

            # while dashing, periodically emit short lances forward
            self.dash_emit_cd -= dt
            if self.dash_emit_cd <= 0:
                self.dash_emit_cd = 0.12
                dv = pg.Vector2(self.vx, self.vy)
                if dv.length_squared() > 1:
                    dv = dv.normalize()
                    # one fast lance, plus two slight spreads
                    for spread in (-0.15, 0.0, 0.15):
                        a = dv.rotate_rad(spread)
                        projectiles.append(Projectile(self.x, self.y, a.x * 260.0, a.y * 260.0, 6, 1, False, sprite_id=None))

            if collided:
                self.state = "charge"
                self.cd = 0.8
            if self.cd <= 0:
                self.state = "charge"
                self.cd = 0.8

@register_boss("ogre_boss")
class OgreBoss(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=50, speed=150.0)
        self.is_boss = True
        self.max_hp = self.hp
        self._state = "charge"
        self._cd = 0.8
        self.vx = 0.0; self.vy = 0.0

    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera | None = None) -> None:
        r = self.rect();
        if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
        pg.draw.rect(surf, (180, 80, 60), r)

    def update(self, dt: float, player_pos: pg.Vector2, walls, projectiles):
        self._cd = max(0.0, self._cd - dt)
        if self._state == "charge":
            if self._cd <= 0.0:
                d = (player_pos - self.center())
                if d.length_squared() > 0:
                    d = d.normalize(); speed = 450.0
                    self.vx, self.vy = d.x*speed, d.y*speed
                    self._cd = 0.6; self._state = "dash"
        else: # dash
            nx, ny, collided = move_and_collide(self.x, self.y, 24, 24, self.vx*dt, self.vy*dt, walls, ox=-12, oy=-12, stop_on_collision=False)
            self.x, self.y = nx, ny
            if collided or self._cd <= 0.0:
                self._state = "charge"; self._cd = 0.8
                for i in range(12):
                    ang = i * (3.14159 * 2 / 12)
                    v = pg.math.Vector2(160.0, 0).rotate_rad(ang)
                    projectiles.append(Projectile(self.x, self.y, v.x, v.y, 6, 1, False, sprite_id=None))
