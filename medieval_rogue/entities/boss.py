from __future__ import annotations
import pygame as pg, math, random
from dataclasses import dataclass
from ..entities.projectile import Projectile


@dataclass
class Boss:
    x: float; y: float; hp: int; name: str = "Boss"
    alive: bool = True
    
    def rect(self) -> pg.Rect: return pg.Rect(int(self.x-10), int(self.y-10), 20, 20)
    
    def center(self) -> pg.Vector2: return pg.Vector2(self.x, self.y)

    def update(self, dt: float, player_pos: pg.Vector2, projectiles: list[Projectile], summons: list) -> None: ...

    def draw(self, surf: pg.Surface) -> None: pg.draw.rect(surf, (200,80,120), self.rect())


class Warden(Boss):     # bouncing + 5-way volley
    def __init__(self, x, y):
        super().__init__(x, y, hp=30, name="Warden")
        self.vx, self.vy = 60.0, 45.0; self.cd = 1.0

    def draw(self, surf: pg.Surface) -> None: pg.draw.rect(surf, (50,220,150), self.rect())

    def update(self, dt, player_pos, projectiles, summons):
        self.x += self.vx*dt; self.y += self.vy*dt
        w, h = 320,180
        if self.x<10 or self.x>w-10: self.vx*=-1
        if self.y<10 or self.y>h-10: self.vy*=-1
        self.cd -= dt
        if self.cd<=0:
            self.cd=1.0
            for ang in (0,72,144,216,288):
                rad = math.radians(ang)
                projectiles.append(Projectile(
                    self.x, self.y, math.cos(rad)*130, math.sin(rad)*130,2,1,False
                ))


class Warlock(Boss):    # bullet rings
    def __init__(self, x, y): super().__init__(x, y, hp=40, name="Warlock"); self.t=0.0

    def draw(self, surf: pg.Surface) -> None: pg.draw.rect(surf, (180,100,220), self.rect())

    def update(self, dt, player_pos, projectiles, summons):
        self.t += dt; self.x += (160-self.x)*0.5*dt; self.y += (90-self.y)*0.5*dt
        if self.t>=1.2:
            self.t=0.0
            base = random.random()*math.tau
            for i in range(10):
                a = base + (i/10.0)*math.tau
                projectiles.append(Projectile(
                    self.x,self.y,math.cos(a)*150,math.sin(a)*150,2,1,False
                ))


class KnightCaptain(Boss):      # telegraphed dash
    def __init__(self, x, y):
        super().__init__(x, y, hp=50, name="Knight Captain")
        self.state="charge"; self.cd=0.8; self.vx=self.vy=0.0
    
    def draw(self, surf: pg.Surface) -> None:
        pg.draw.rect(surf, (200,180,80) if self.state=="charge" else (220,140,60), self.rect())

    def update(self, dt, player_pos, projectiles, summons):
        if self.state=="charge":
            self.cd-=dt
            if self.cd<0:
                d = (player_pos - self.center())
                if d.length_squared()>0:
                    d = d.normalize()
                    self.vx,self.vy = d.x*260, d.y*260; self.cd=0.6; self.state="dash"
        else:
            self.x+=self.vx*dt; self.y+=self.vy*dt; self.cd-=dt
            if self.cd<=0: self.state="charge"; self.cd=0.8

BOSSES = [Warden, Warlock, KnightCaptain]
