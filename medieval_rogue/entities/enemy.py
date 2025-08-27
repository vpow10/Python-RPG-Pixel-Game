from __future__ import annotations
import pygame as pg, random
from dataclasses import dataclass
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera
from medieval_rogue.entities.base import Entity
from medieval_rogue.entities.enemy_registry import register_enemy


@dataclass
class Enemy(Entity):
    hp: int = 1
    speed: float = 40.0
    touch_damage: int = 1
    
    def rect(self):
        return pg.Rect(int(self.x-8), int(self.y-8), 16, 16)
    
    def update(self, dt, player_pos, walls, projectiles, **kwargs):
        pass
    
@register_enemy("slime")
class Slime(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=3, speed=120.0)
        
    def draw(self, surf, camera: Camera=None):
        r = self.rect();
        if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
        pg.draw.ellipse(surf, (100,200,100), r)
        
    def update(self, dt, player_pos, walls, projectiles):
        v = player_pos - self.center()
        if v.length_squared() > 1:
            step = v.normalize() * self.speed * dt
            nx, ny, _ = move_and_collide(self.x, self.y, 10, 10, step.x, step.y, walls, ox=-5, oy=-5, stop_on_collision=False)
            self.x, self.y = nx, ny

@register_enemy("bat")
class Bat(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=1, speed=240.0)

    def draw(self, surf, camera: Camera=None):
        r = self.rect();
        if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
        pg.draw.rect(surf, (120,120,220), r)

    def update(self, dt, player_pos, walls, projectiles):
        v = player_pos - self.center()
        if v.length_squared() > 1:
            jitter = pg.Vector2(random.uniform(-0.5,0.5), random.uniform(-0.5,0.5))*0.3
            step = (v.normalize() + jitter).normalize() * self.speed * dt
            nx, ny, _ = move_and_collide(self.x, self.y, 10, 10, step.x, step.y, walls, ox=-5, oy=-5, stop_on_collision=False)
            self.x, self.y = nx, ny

@register_enemy("skeleton")
class Skeleton(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=3, speed=150.0)
        self.shoot_cd = random.uniform(0.5, 1.2)

    def draw(self, surf, camera: Camera=None):
        r = self.rect();
        if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
        pg.draw.rect(surf, (220,220,220), r)

    def update(self, dt, player_pos, walls, projectiles):
        v = player_pos - self.center(); dist = v.length()
        step = pg.Vector2(0,0)
        if dist > 1:
            n = v.normalize()
            if dist > 420: step = n * (self.speed * dt)
            elif dist < 300: step = -n * (self.speed * dt)
        nx, ny, _ = move_and_collide(self.x, self.y, 10, 10, step.x, step.y, walls, ox=-5, oy=-5, stop_on_collision=False)
        self.x, self.y = nx, ny
        self.shoot_cd -= dt
        if self.shoot_cd <= 0 and dist > 1:
            self.shoot_cd = 1.2
            d = v.normalize(); speed = 360.0
            projectiles.append(Projectile(self.x, self.y, d.x*speed, d.y*speed, 2, 1, False))
