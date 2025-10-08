from __future__ import annotations
import pygame as pg, math, random
from dataclasses import dataclass
from medieval_rogue import settings as S
from assets.sprite_manager import _load_image
from medieval_rogue.dungeon.room import inset_rect

_TORCH = None
_LIGHT_SPRITES: dict[tuple[int,int,int], pg.Surface] = {}

def _torch_img() -> pg.Surface:
    global _TORCH
    if _TORCH is None:
        try:
            _TORCH = _load_image(['assets','sprites','props','torch.png'])
        except Exception:
            s = pg.Surface((32, 32), pg.SRCALPHA)
            pg.draw.rect(s, (200,180,80), (12,4,8,24))
            _TORCH = s
    return _TORCH

def _radial_brightness(radius: int, inner: int, outer: int) -> pg.Surface:
    key = (radius, inner, outer)
    if key in _LIGHT_SPRITES:
        return _LIGHT_SPRITES[key]
    d = radius * 2
    surf = pg.Surface((d, d), pg.SRCALPHA)
    cx = cy = radius
    for y in range(d):
        for x in range(d):
            r = ((x - cx)**2 + (y - cy)**2) ** 0.5
            t = min(1.0, r / radius)
            v = int(outer + (inner - outer) * t)
            surf.set_at((x, y), (v, v, v, 255))
    _LIGHT_SPRITES[key] = surf
    return surf

@dataclass
class Torch:
    x: int; y: int
    phase: float = 0.0
    speed: float = 3.5
    base: int = 24
    amp: int = 10

def compute_torches_for_room(room) -> list[Torch]:
    inner = inset_rect(room.world_rect, S.ROOM_INSET)
    torches: list[Torch] = []
    pad = 32
    candidates = [
        (inner.centerx, inner.top + 16),
        (inner.left + pad, inner.centery-16),
        (inner.right - pad, inner.centery-16),
        (inner.centerx, inner.bottom - 16),
    ]
    for (x, y) in candidates:
        ok = True
        for side, d in room.doors.items():
            if side in ("N","S") and abs(y - (inner.top if side=="N" else inner.bottom)) < 24:
                if d.rect.left <= x <= d.rect.right:
                    ok = False; break
            if side in ("W","E") and abs(x - (inner.left if side=="W" else inner.right)) < 24:
                if d.rect.top <= y <= d.rect.bottom:
                    ok = False; break
        if ok:
            torches.append(Torch(x, y, phase=random.uniform(0.0, 6.283)))
    return torches

def update_torches(torches: list[Torch], dt: float) -> None:
    for t in torches:
        t.phase += t.speed * dt

def draw_torches(surf: pg.Surface, camera, torches: list[Torch]) -> None:
    img = _torch_img()
    for t in torches:
        sx, sy = camera.world_to_screen(t.x, t.y)
        rect = img.get_rect(midbottom=(int(sx), int(sy)))
        surf.blit(img, rect)

def apply_lighting(surf: pg.Surface, camera, torches: list[Torch]) -> None:
    sw, sh = surf.get_size()
    ambient = int(255 * float(getattr(S, "AMBIENT_LIGHT", 0.8)))
    lightmap = pg.Surface((sw, sh), pg.SRCALPHA)
    lightmap.fill((ambient, ambient, ambient, 255))
    radius = int(S.LIGHT_RADIUS)

    for t in torches:
        flicker = max(0, min(255, int(255 - (t.base + int(t.amp * math.sin(t.phase))))))
        inner = min(255, ambient + flicker)
        sprite = _radial_brightness(radius, inner=ambient, outer=inner)
        sx, sy = camera.world_to_screen(t.x, t.y)
        rect = sprite.get_rect(center=(int(sx), int(sy) - 16))
        lightmap.blit(sprite, rect, special_flags=pg.BLEND_RGBA_MAX)

    surf.blit(lightmap, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
