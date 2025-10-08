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
                6, 1, False, sprite_id=None, color=(255,103,255)
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
        super().__init__(x, y, hp=50, speed=0.0, sprite_id="knight_captain")
        self.is_boss = True
        self.max_hp = self.hp
        self.state = "charge"
        self.cd = 0.8
        self.vx = self.vy = 0.0
        self.dash_emit_cd = 0.12
        self.dash_timer = 0.0
        self.name = "Knight Captain"

        FRAME_W, FRAME_H = 96, 96
        idle_frames = load_strip(['assets','sprites','bosses','knight_captain_idle.png'], FRAME_W, FRAME_H)
        dash_frames = load_strip(['assets','sprites','bosses','knight_captain_dash.png'], FRAME_W, FRAME_H)

        self.anims = {
            "idle": AnimatedSprite(idle_frames, fps=2, loop=True, anchor='center'),
            "dash": AnimatedSprite(dash_frames, fps=8, loop=True, anchor='center')
        }
        self.sprite = self.anims["idle"]

    def _set_anim(self, name: str):
        nxt = self.anims.get(name)
        if nxt and self.sprite is not nxt:
            nxt.paused = False; nxt.idx = 0; nxt.t = 0.0
            self.sprite = nxt

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
            pg.draw.rect(surf, (200,180,80) if self.state=="charge" else (220,140,60), r)

    def update(self, dt, player_pos, walls, projectiles):
        if self.state == "charge":
            self._set_anim("idle")
            self.cd -= dt
            if self.cd < 0:
                d = (player_pos - self.center())
                if d.length_squared() > 0:
                    d = d.normalize()
                    self.vx, self.vy = d.x*480, d.y*480
                    self.cd = 0.8
                    self.dash_timer = 0.65
                    self.state = "dash"
                    self.dash_emit_cd = 0.08
        else:  # dash
            self._set_anim("dash")
            dx = self.vx * dt
            dy = self.vy * dt
            nx, ny, collided = move_and_collide(self.x, self.y, 32, 32,
                                               dx, dy, walls, ox=-16, oy=-16, stop_on_collision=False)
            self.x, self.y = nx, ny

            # Emit lances periodically
            self.dash_emit_cd -= dt
            if self.dash_emit_cd <= 0:
                self.dash_emit_cd = 0.12
                dv = pg.Vector2(self.vx, self.vy)
                if dv.length_squared() > 1:
                    dv = dv.normalize()
                    for spread in (-0.25, 0.0, 0.25):
                        a = dv.rotate_rad(spread)
                        projectiles.append(Projectile(
                            self.x, self.y,
                            a.x * 360.0, a.y * 360.0,
                            6, 1, False,
                            sprite_id=None,
                            color=(87,191,56)
                        ))

            # End dash after timer or collision
            self.dash_timer -= dt
            if self.dash_timer <= 0 or collided:
                self.state = "charge"
                self.cd = 0.8

        # Update animation
        if self.sprite:
            self.sprite.update(dt)

@register_boss("ogre_warrior")
class OgreWarrior(Enemy):
    def __init__(self, x, y, **opts):
        super().__init__(x, y, hp=30, speed=100.0, sprite_id="ogre_warrior")
        self.is_boss = True
        self.max_hp = self.hp
        self._state = "charge"
        self._cd = 1.6
        self.vx = 0.0
        self.vy = 0.0
        self.dash_timer = 0.0
        self.name = "Ogre Warrior"

        FRAME_W, FRAME_H = 96, 96
        walk_frames = load_strip(['assets','sprites','bosses','ogre_warrior_walk.png'], FRAME_W, FRAME_H)
        dash_frames = load_strip(['assets','sprites','bosses','ogre_warrior_dash.png'], FRAME_W, FRAME_H)

        self.anims = {
            "walk": AnimatedSprite(walk_frames, fps=4, loop=True, anchor='center'),
            "dash": AnimatedSprite(dash_frames, fps=8, loop=True, anchor='center')
        }
        self.sprite = self.anims["walk"]

    def _set_anim(self, name: str):
        nxt = self.anims.get(name)
        if nxt and self.sprite is not nxt:
            nxt.paused = False; nxt.idx = 0; nxt.t = 0.0
            self.sprite = nxt

    def rect(self) -> pg.Rect:
        return pg.Rect(int(self.x-16), int(self.y-16), 32, 32)

    def draw(self, surf: pg.Surface, camera: Camera | None = None) -> None:
        if self.sprite:
            self.sprite.draw(surf, self.x, self.y, camera=camera)
        else:
            r = self.rect()
            if camera is not None:
                sx, sy = camera.world_to_screen(r.x, r.y)
                r = pg.Rect(sx, sy, r.w, r.h)
            pg.draw.rect(surf, (180, 80, 60), r)

    def update(self, dt: float, player_pos: pg.Vector2, walls, projectiles):
        self._cd = max(0.0, self._cd - dt)

        if self._state == "charge":
            self._set_anim("walk")

            to_player = (player_pos - self.center())
            if to_player.length_squared() > 1e-6:
                dir = to_player.normalize()
            else:
                dir = pg.Vector2()

            walk_speed = self.speed
            dx, dy = dir.x * walk_speed * dt, dir.y * walk_speed * dt
            nx, ny, _ = move_and_collide(
                self.x, self.y, 24, 24, dx, dy,
                walls, ox=-12, oy=-12, stop_on_collision=True
            )
            self.x, self.y = nx, ny

            if self._cd <= 0.0 and dir.length_squared() > 0.0:
                dash_speed = 500.0
                self.vx, self.vy = dir.x * dash_speed, dir.y * dash_speed
                self._cd = 1.6
                self.dash_timer = 0.3
                self._state = "dash"

        else:  # dash
            self._set_anim("dash")
            dx, dy = self.vx * dt, self.vy * dt
            nx, ny, collided = move_and_collide(
                self.x, self.y, 24, 24, dx, dy,
                walls, ox=-12, oy=-12, stop_on_collision=False
            )
            self.x, self.y = nx, ny

            self.dash_timer -= dt
            if collided or self.dash_timer <= 0:
                self._state = "charge"
                self._cd = 1.6
                self.vx = 0.0
                self.vy = 0.0

                for i in range(12):
                    ang = i * (math.tau / 12)
                    v = pg.Vector2(160.0, 0).rotate_rad(ang)
                    projectiles.append(
                        Projectile(self.x, self.y, v.x, v.y, 6, 1, False, sprite_id=None)
                    )

        if self.sprite:
            self.sprite.update(dt)
