from __future__ import annotations
import pygame as pg, random, math
from dataclasses import dataclass
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera
from medieval_rogue.entities.base import Entity
from medieval_rogue.entities.enemy_registry import register_enemy
from medieval_rogue import settings as S
from assets.sprite_manager import AnimatedSprite, load_strip


@dataclass
class Enemy(Entity):
    hp: int = 1
    speed: float = 40.0
    touch_damage: int = 1
    sprite: AnimatedSprite | None = None
    
    def __post_init__(self):
        try:
            frames = load_strip(['assets','sprites','enemies', f'{self.sprite_id}_idle.png'], 64, 64)
            self.sprite = AnimatedSprite(frames, fps=6, loop=True, anchor='bottom')
        except Exception:
            self.sprite = None

    def rect(self):
        w, h = S.ENEMY_HITBOX
        return pg.Rect(int(self.x-w//2), int(self.y-h), w, h)

    def update(self, dt, player_pos, walls, projectiles, **kwargs):
        pass

@register_enemy("slime", sprite_id="slime")
class Slime(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, sprite_id="slime", hp=3, speed=90.0)

    def draw(self, surf, camera: Camera=None):
        if self.sprite:
            self.sprite.draw(surf, self.x, self.y, camera=camera)
        else:
            r = self.rect();
            if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
            pg.draw.ellipse(surf, (100,200,100), r)

    def update(self, dt, player_pos, walls, projectiles):
        v = player_pos - self.center()
        w, h = S.ENEMY_HITBOX
        ox = -w//2
        oy = -h
        if v.length_squared() > 1:
            step = v.normalize() * self.speed * dt
            nx, ny, collided = move_and_collide(self.x, self.y, w, h, step.x, step.y, walls, ox=ox, oy=oy, stop_on_collision=False)
            if collided:
                # try axis-aligned fallbacks and pick the one that moves further
                nx_h, ny_h, _ = move_and_collide(self.x, self.y, w, h, step.x, 0, walls, ox=ox, oy=oy, stop_on_collision=False)
                nx_v, ny_v, _ = move_and_collide(self.x, self.y, w, h, 0, step.y, walls, ox=ox, oy=oy, stop_on_collision=False)
                dist_h = (nx_h - self.x)**2 + (ny_h - self.y)**2
                dist_v = (nx_v - self.x)**2 + (ny_v - self.y)**2
                if dist_h >= dist_v and dist_h > 0:
                    nx, ny = nx_h, ny_h
                elif dist_v > 0:
                    nx, ny = nx_v, ny_v
                else:
                    # if both blocked, try small random sidestep
                    ang = random.uniform(0, math.tau)
                    sidex = math.cos(ang) * (self.speed * dt * 0.5)
                    sidey = math.sin(ang) * (self.speed * dt * 0.5)
                    nx, ny, _ = move_and_collide(self.x, self.y, w, h, sidex, sidey, walls, ox=ox, oy=oy, stop_on_collision=False)
            self.x, self.y = nx, ny

@register_enemy("bat", sprite_id="bat")
class Bat(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=1, sprite_id="bat", speed=180.0)

    def draw(self, surf, camera: Camera=None):
        if hasattr(self, 'sprite') and self.sprite:
            self.sprite.draw(surf, self.x, self.y, camera=camera)
        else:
            r = self.rect();
            if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
            pg.draw.rect(surf, (120,120,220), r)

    def update(self, dt, player_pos, walls, projectiles):
        v = player_pos - self.center()
        w, h = S.ENEMY_HITBOX
        ox = -w//2
        oy = -h
        if v.length_squared() > 1:
            jitter = pg.Vector2(random.uniform(-0.5,0.5), random.uniform(-0.5,0.5))*0.5
            step = (v.normalize() + jitter).normalize() * self.speed * dt
            nx, ny, collided = move_and_collide(self.x, self.y, w, h, step.x, step.y, walls, ox=ox, oy=oy, stop_on_collision=False)
            if collided:
                # sliding fallback (horizontal / vertical)
                nx_h, ny_h, _ = move_and_collide(self.x, self.y, w, h, step.x, 0, walls, ox=ox, oy=oy, stop_on_collision=False)
                nx_v, ny_v, _ = move_and_collide(self.x, self.y, w, h, 0, step.y, walls, ox=ox, oy=oy, stop_on_collision=False)
                if (nx_h - self.x)**2 + (ny_h - self.y)**2 >= (nx_v - self.x)**2 + (ny_v - self.y)**2:
                    nx, ny = nx_h, ny_h
                else:
                    nx, ny = nx_v, ny_v
            self.x, self.y = nx, ny

@register_enemy("skeleton", sprite_id="skeleton")
class Skeleton(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=3, sprite_id="skeleton", speed=120.0)
        self.shoot_cd = random.uniform(0.5, 1.2)

    def draw(self, surf, camera: Camera=None):
        if hasattr(self, 'sprite') and self.sprite:
            self.sprite.draw(surf, self.x, self.y, camera=camera)
        else:
            r = self.rect();
            if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
            pg.draw.rect(surf, (220,220,220), r)

    def update(self, dt, player_pos, walls, projectiles):
        v = player_pos - self.center()
        w, h = S.ENEMY_HITBOX
        ox = -w//2
        oy = -h
        dist = v.length()
        step = pg.Vector2(0,0)
        if dist > 1:
            n = v.normalize()
            if dist > 420:
                step = n * (self.speed * dt)
            elif dist < 300:
                step = -n * (self.speed * dt)

        nx, ny, collided = move_and_collide(self.x, self.y, w, h, step.x, step.y, walls, ox=ox, oy=oy, stop_on_collision=False)
        if collided:
            # try axis fallback
            nx_h, ny_h, _ = move_and_collide(self.x, self.y, w, h, step.x, 0, walls, ox=ox, oy=oy, stop_on_collision=False)
            nx_v, ny_v, _ = move_and_collide(self.x, self.y, w, h, 0, step.y, walls, ox=ox, oy=oy, stop_on_collision=False)
            if (nx_h - self.x)**2 + (ny_h - self.y)**2 >= (nx_v - self.x)**2 + (ny_v - self.y)**2:
                nx, ny = nx_h, ny_h
            else:
                nx, ny = nx_v, ny_v
        self.x, self.y = nx, ny

        self.shoot_cd -= dt
        if self.shoot_cd <= 0 and dist > 1:
            self.shoot_cd = 1.2
            d = v.normalize(); speed = 360.0
            projectiles.append(Projectile(self.x, self.y, d.x*speed, d.y*speed, 6, 1, False))
