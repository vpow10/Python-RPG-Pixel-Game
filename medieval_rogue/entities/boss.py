from __future__ import annotations
import pygame as pg, math, random
from dataclasses import dataclass
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera
from medieval_rogue.entities.enemy_registry import register
from medieval_rogue.entities.enemy import Enemy


@register("ogre_boss")
class OgreBoss(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x,y,hp=40,speed=0.6)
        self.is_boss = True
        self.drop_table = opts.get("drop_table", [{"item":"Chestplate","chance":1.0}])

    def update(self, dt, player_pos, walls, projectiles):
        pass

@dataclass
class Boss:
    x: float; y: float; max_hp: int; name: str = "Boss"; hp: int = 0
    alive: bool = True; touch_damage: int = 1

    def rect(self) -> pg.Rect: return pg.Rect(int(self.x-10), int(self.y-10), 20, 20)

    def center(self) -> pg.Vector2: return pg.Vector2(self.x, self.y)

    def update(self, dt: float, player_pos: pg.Vector2, projectiles: list[Projectile], summons: list) -> None: ...

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (200,80,120), r)


class Warden(Boss):     # bouncing + 5-way volley
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=30, name="Warden")
        self.vx, self.vy = 60.0, 45.0; self.cd = 1.0; self.hp = self.max_hp

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (50,220,150), r)

    def update(self, dt, player_pos, projectiles, summons, walls):
        dx = self.vx * dt
        dy = self.vy * dt
        nx, ny, _ = move_and_collide(self.x, self.y, 20, 20, dx, dy, walls, ox=-10, oy=-10, stop_on_collision=False)
        if nx != self.x + dx:
            self.vx *= -1
        if ny != self.y + dy:
            self.vy *= -1
        self.x, self.y = nx, ny
        self.cd -= dt
        if self.cd<=0:
            self.cd=1.0
            for ang in (0,72,144,216,288):
                rad = math.radians(ang)
                projectiles.append(Projectile(
                    self.x, self.y, math.cos(rad)*130, math.sin(rad)*130,2,1,False
                ))


class Warlock(Boss):    # bullet rings
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=40, name="Warlock"); self.t=0.0; self.hp=self.max_hp

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (180,100,220), r)

    def update(self, dt, player_pos, projectiles, summons, walls):
        self.t += dt; self.x += (160-self.x)*0.5*dt; self.y += (90-self.y)*0.5*dt
        if self.t>=0.8:
            self.t=0.0
            base = random.random()*math.tau
            for i in range(10):
                a = base + (i/10.0)*math.tau
                projectiles.append(Projectile(
                    self.x,self.y,math.cos(a)*150,math.sin(a)*150,2,1,False
                ))


class KnightCaptain(Boss):      # telegraphed dash
    def __init__(self, x, y):
        super().__init__(x, y, max_hp=50, name="Knight Captain")
        self.state="charge"; self.cd=0.8; self.vx=self.vy=0.0; self.hp=self.max_hp

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (200,180,80) if self.state=="charge" else (220,140,60), r)

    def update(self, dt, player_pos, projectiles, summons, walls):
        if self.state=="charge":
            self.cd-=dt
            if self.cd<0:
                d = (player_pos - self.center())
                if d.length_squared()>0:
                    d = d.normalize()
                    self.vx,self.vy = d.x*260, d.y*260; self.cd=0.6; self.state="dash"
        else:
            dx = self.vx * dt
            dy = self.vy * dt
            nx, ny, collided = move_and_collide(self.x, self.y, 20, 20, dx, dy, walls, ox=-10, oy=-10, stop_on_collision=False)
            self.x, self.y = nx, ny
            if collided:
                self.state = "charge"
                self.cd = 0.8
            if self.cd<=0: self.state="charge"; self.cd=0.8

BOSSES = [Warden, Warlock, KnightCaptain]
