from __future__ import annotations
import pygame as pg, random
from dataclasses import dataclass
from ..entities.projectile import Projectile
from .utilities import move_and_collide


@dataclass
class Enemy:
    x: float; y: float; hp: int; speed: float
    touch_damage: int = 1
    alive: bool = True

    def rect(self) -> pg.Rect: return pg.Rect(int(self.x-5), int(self.y-5), 10, 10)

    def center(self) -> pg.Vector2: return pg.Vector2(self.x, self.y)

    def update(self, dt:float, player_pos: pg.Vector2, projectiles: list[Projectile], walls: list[pg.Rect]) -> None: ...

    def draw(self, surf: pg.Surface) -> None: pg.draw.rect(surf, (160,70,70), self.rect())


class Slime(Enemy):
    def __init__(self, x, y): super().__init__(x, y, hp=2, speed=40.0)

    def draw(self, surf: pg.Surface) -> None: pg.draw.rect(surf, (90,200,120), self.rect())

    def update(self, dt, player_pos, projectiles, walls):
        v = player_pos - self.center()
        if v.length_squared() > 1:
            step = v.normalize() * self.speed * dt
            nx, ny, _ = move_and_collide(self.x, self.y, 10, 10, step.x, step.y, walls, ox=-5, oy=-5, stop_on_collision=False)
            self.x, self.y = nx, ny


class Bat(Enemy):
    def __init__(self, x, y): super().__init__(x, y, hp=1, speed=80.0)

    def draw(self, surf: pg.Surface) -> None: pg.draw.rect(surf, (120,120,220), self.rect())

    def update(self, dt, player_pos, projectiles, walls):
        v = player_pos - self.center()
        if v.length_squared() > 1:
            jitter = pg.Vector2(random.uniform(-0.5,0.5), random.uniform(-0.5,0.5))*0.3
            step = (v.normalize() + jitter).normalize() * self.speed * dt
            nx, ny, _ = move_and_collide(self.x, self.y, 10, 10, step.x, step.y, walls, ox=-5, oy=-5, stop_on_collision=False)
            self.x, self.y = nx, ny


class Skeleton(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=3, speed=50.0)
        self.shoot_cd = random.uniform(0.5, 1.2)

    def draw(self, surf: pg.Surface) -> None: pg.draw.rect(surf, (220,220,220), self.rect())

    def update(self, dt, player_pos, projectiles, walls):
        v = player_pos - self.center()
        dist = v.length()

        step = pg.Vector2(0, 0)
        if dist > 1:
            n = v.normalize()
            if dist > 80:
                step = n * (self.speed * dt)
            elif dist < 60:
                step = -n * (self.speed * dt)

        nx, ny, _ = move_and_collide(self.x, self.y, 10, 10, step.x, step.y, walls, ox=-5, oy=-5, stop_on_collision=False)
        self.x, self.y = nx, ny

        self.shoot_cd -= dt
        if self.shoot_cd <= 0 and dist > 1:
            self.shoot_cd = 1.2
            d = v.normalize()
            speed = 120.0
            projectiles.append(Projectile(self.x, self.y, d.x * speed, d.y * speed, 2, 1, False))


ENEMY_TYPES = [Slime, Bat, Skeleton]
