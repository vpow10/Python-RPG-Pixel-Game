from __future__ import annotations
import pygame as pg
from dataclasses import dataclass, field
from typing import List
from medieval_rogue import settings as S
from medieval_rogue.entities.projectile import Projectile
from medieval_rogue.entities.utilities import move_and_collide
from medieval_rogue.camera import Camera
from assets.sprite_manager import AnimatedSprite, _load_image, slice_sheet, load_strip


@dataclass
class PlayerStats:
    hp: int = S.PLAYER_BASE_HP
    speed: float = S.PLAYER_BASE_SPEED
    firerate: float = S.PLAYER_BASE_FIRERATE
    proj_speed: float = S.PLAYER_BASE_PROJ_SPEED
    damage: float = S.PLAYER_BASE_DAMAGE

@dataclass
class Player:
    x: float; y: float
    stats: PlayerStats = field(default_factory=PlayerStats)
    hp: int = field(init=False)
    fire_cd: float = 0.0
    invuln_timer: float = 0.0
    inventory: List[str] = field(default_factory=list)
    sprite_id: str = "archer"

    def __post_init__(self):
        self.hp = self.stats.hp
        self.sfx_shot = None
        
        # Load animations 
        idle_frames = load_strip(['assets', 'sprites', 'player', f'{self.sprite_id}_idle.png'], 64, 64)
        walk_frames  = load_strip(['assets', 'sprites', 'player', f'{self.sprite_id}_walk.png'],  64, 64)
        shoot_frames = load_strip(['assets', 'sprites', 'player', f'{self.sprite_id}_shoot.png'], 64, 64)
        
        self.anims = {
            "idle":  AnimatedSprite(idle_frames,  fps=6,  loop=True,  anchor='bottom'),
            "walk":  AnimatedSprite(walk_frames,  fps=10, loop=True,  anchor='bottom'),
            "shoot": AnimatedSprite(shoot_frames, fps=12, loop=False, anchor='bottom'),
        }
        self.sprite = self.anims["idle"]
        self.facing_left = False
        
    def _set_anim(self, name: str):
        nxt = self.anims[name]
        if self.sprite is not nxt:
            nxt.paused = False; nxt.idx = 0; nxt.t = 0.0
            self.sprite = nxt

    @property
    def speed(self) -> float: return self.stats.speed
    @property
    def firerate(self) -> float: return self.stats.firerate
    @property
    def proj_speed(self) -> float: return self.stats.proj_speed
    @property
    def damage(self) -> float: return self.stats.damage

    def rect(self) -> pg.Rect:
        w,h = S.PLAYER_HITBOX
        return pg.Rect(int(self.x-w//2), int(self.y-h), w, h)

    def center(self) -> pg.Vector2:
        r = self.rect(); return pg.Vector2(r.centerx, r.centery)

    def set_position(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.rect()

    def update(self, dt: float, keys, mouse_buttons, mouse_pos, walls: list[pg.Rect], projectiles: list[Projectile]) -> None:
        self.sprite.update(dt)
        is_moving = move.length_squared() > 0
        self._set_anim("walk" if is_moving else "idle")
        self.facing_left = mouse_pos[0] < self.x
        w, h = S.PLAYER_HITBOX
        ox = -w//2
        oy = -h
        move = pg.Vector2(0,0)
        if keys[pg.K_w] or keys[pg.K_UP]: move.y -= 1
        if keys[pg.K_s] or keys[pg.K_DOWN]: move.y += 1
        if keys[pg.K_a] or keys[pg.K_LEFT]: move.x -= 1
        if keys[pg.K_d] or keys[pg.K_RIGHT]: move.x += 1
        if is_moving > 0:
            move = move.normalize() * self.speed * dt
            new_x, new_y, _ = move_and_collide(self.x, self.y, w, h, move.x, move.y, walls, ox=ox, oy=oy, stop_on_collision=False)
            self.x, self.y = new_x, new_y
        self.fire_cd = max(0.0, self.fire_cd - dt)
        if mouse_buttons[0] and self.fire_cd <= 0.0:
            if self.sfx_shot: self.sfx_shot.play()
            self._set_anim("shoot")
            self.sprite.loop = False
            self.sprite.paused = False
            dir_vec = pg.Vector2(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
            if dir_vec.length_squared() > 0:
                v = dir_vec.normalize() * self.proj_speed
                projectiles.append(Projectile(self.x, self.y, v.x, v.y, 6, self.damage, True))
                self.fire_cd = 1.0 / self.firerate
        if self.sprite is self.anims["shoot"] and self.sprite.paused:
            self._set_anim("walk" if is_moving else "idle")
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

    def take_damage(self, dmg: int):
        if self.invuln_timer <= 0:
            self.hp -= dmg
            self.invuln_timer = 1.0
            return True
        return False

    def apply_item(self, item):
        item.apply(self)
        self.inventory.append(item.name)

    def draw(self, surf: pg.Surface, camera: Camera=None) -> None:
        if self.invuln_timer > 0 and int(self.invuln_timer * 10) % 2 == 0:
            return
        if hasattr(self, 'sprite') and self.sprite:
            self.sprite.draw(surf, self.x, self.y, camera=camera, flip_x=self.facing_left)
        else:
            r = self.rect();
            if camera is not None: sx, sy = camera.world_to_screen(r.x, r.y); r = pg.Rect(sx, sy, r.w, r.h)
            pg.draw.rect(surf, (60,120,80), r)
            pg.draw.rect(surf, (30,80,50), (r.x, r.y-3, r.w, 3))
