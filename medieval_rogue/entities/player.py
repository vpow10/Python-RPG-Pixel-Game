from __future__ import annotations
import pygame as pg
from dataclasses import dataclass
from .. import settings as S
from .projectile import Projectile
from .utilities import move_and_collide


@dataclass
class Player:
    x: float; y: float
    hp: int = S.PLAYER_BASE_HP
    speed: float = S.PLAYER_BASE_SPEED
    firerate: float = S.PLAYER_BASE_FIRERATE
    proj_speed: float = S.PLAYER_BASE_PROJ_SPEED
    damage: int = S.PLAYER_BASE_DAMAGE
    fire_cd: float = 0.0
    invuln_timer: float = 0.0

    def __post_init__(self):
        from ..assets.sound_manager import load_sounds
        self.sfx_shot = load_sounds()["shot"]
        self.sfx_shot.set_volume(0.2)

    def center(self) -> pg.Vector2: return pg.Vector2(self.x, self.y)

    def rect(self) -> pg.Rect: return pg.Rect(int(self.x-5), int(self.y-6), 10, 12)

    def update(self, dt:float, keys, mouse_pos, mouse_buttons, projectiles: list[Projectile], walls: list[pg.Rect]) -> None:
        vx = (keys[pg.K_d] - keys[pg.K_a]); vy = (keys[pg.K_s] - keys[pg.K_w])
        move = pg.Vector2(vx, vy)
        if move.length_squared() > 0:
            move = move.normalize() * self.speed * dt
            new_x, new_y, _ = move_and_collide(self.x, self.y, 10, 12, move.x, move.y, walls, ox=-5, oy=-6, stop_on_collision=False)
            self.x, self.y = new_x, new_y

        self.fire_cd = max(0.0, self.fire_cd - dt)
        if mouse_buttons[0] and self.fire_cd <= 0.0:
            self.sfx_shot.play()
            dir_vec = pg.Vector2(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
            if dir_vec.length_squared() > 0:
                v = dir_vec.normalize() * self.proj_speed
                projectiles.append(Projectile(self.x, self.y, v.x, v.y, 2, self.damage, True))
                self.fire_cd = 1.0 / self.firerate
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

    def take_damage(self, dmg: int):
        if self.invuln_timer <= 0:
            self.hp -= dmg
            self.invuln_timer = 1.0
            return True
        return False

    def draw(self, surf: pg.Surface) -> None:
        if self.invuln_timer > 0 and int(self.invuln_timer * 10) % 2 == 0:
            return      # skip draw every other frame
        r = self.rect()
        pg.draw.rect(surf, (60,120,80), r)                      # body
        pg.draw.rect(surf, (30,80,50), (r.x, r.y-3, r.w, 3))    # hood
