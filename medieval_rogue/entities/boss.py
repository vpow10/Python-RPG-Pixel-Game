from __future__ import annotations
import pygame as pg, random, math
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera
from medieval_rogue.entities.enemy import Enemy
from medieval_rogue.entities.enemy_registry import register_boss


@register_boss("warden")
class Warden(Enemy):     # bouncing + 5-way volley
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=30, speed=60.0)
        self.is_boss = True
        self.max_hp = self.hp
        self.vx = 60.0
        self.vy = 45.0
        self.cd = 1.0
        
    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (50,220,150), r)

    def update(self, dt, player_pos, walls, projectiles):
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

@register_boss("warlock")
class Warlock(Enemy):    # bullet rings
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=40, speed=0.0);
        self.t=0.0;
        self.is_boss = True
        self.max_hp=self.hp
        
    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (180,100,220), r)

    def update(self, dt, player_pos, walls, projectiles):
        self.t += dt; self.x += (160-self.x)*0.5*dt; self.y += (90-self.y)*0.5*dt
        if self.t>=0.8:
            self.t=0.0
            base = random.random()*math.tau
            for i in range(10):
                a = base + (i/10.0)*math.tau
                projectiles.append(Projectile(
                    self.x,self.y,math.cos(a)*150,math.sin(a)*150,2,1,False
                ))

@register_boss("knight_captain")
class KnightCaptain(Enemy):      # telegraphed dash
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=50, speed=0.0)
        self.is_boss = True
        self.max_hp=self.hp
        self.state="charge";
        self.cd=0.8;
        self.vx=self.vy=0.0;
        
    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera = None) -> None:
        r = self.rect()
        if camera is not None:
            screen_pos = camera.world_to_screen(r.x, r.y)
            r = pg.Rect(screen_pos[0], screen_pos[1], r.w, r.h)
        pg.draw.rect(surf, (200,180,80) if self.state=="charge" else (220,140,60), r)

    def update(self, dt, player_pos, walls, projectiles):
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

@register_boss("ogre_boss")
class OgreBoss(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=50, speed=60.0)
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
                    d = d.normalize(); speed = 260.0
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
                    projectiles.append(Projectile(self.x, self.y, v.x, v.y, 2, 1, False))

BOSSES = [
    "warden", "warlock", "knight_captain", "ogre_boss"
]
