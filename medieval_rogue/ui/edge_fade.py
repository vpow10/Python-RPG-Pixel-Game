from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.dungeon.room import inset_rect

def _make_hstrip(width: int) -> pg.Surface:
    width = max(1, int(width))
    surf = pg.Surface((width, 1), pg.SRCALPHA)
    for x in range(width):
        a = int(255 * (x / (width - 1 if width > 1 else 1)))
        surf.set_at((x, 0), (0, 0, 0, a))
    return surf

_HSTRIP = None
_VSTRIP = None

def _ensure_strips():
    global _HSTRIP, _VSTRIP
    if _HSTRIP is None or _HSTRIP.get_width() != int(S.EDGE_FADE):
        _HSTRIP = _make_hstrip(int(S.EDGE_FADE))
        _VSTRIP = pg.transform.rotate(_HSTRIP, 90)

def draw_edge_fade(screen: pg.Surface, camera, room_rect_world: pg.Rect) -> None:
    fade = int(S.EDGE_FADE)
    if fade <= 0:
        return
    _ensure_strips()

    sw, sh = screen.get_width(), screen.get_height()
    screen_rect = pg.Rect(0, 0, sw, sh)

    inner_world = inset_rect(room_rect_world, S.ROOM_INSET)
    tl = camera.world_to_screen(inner_world.left, inner_world.top)
    br = camera.world_to_screen(inner_world.right, inner_world.bottom)
    room_scr = pg.Rect(min(tl[0], br[0]), min(tl[1], br[1]),
                       abs(br[0] - tl[0]), abs(br[1] - tl[1]))
    room_scr = room_scr.clip(screen_rect)

    start_shift = int(getattr(S, "EDGE_FADE_START_SHIFT", 0))
    start_rect = room_scr.inflate(2 * start_shift, 2 * start_shift).clip(screen_rect)

    mask = pg.Surface((sw, sh), pg.SRCALPHA)

    if start_rect.left > 0:
        w = min(fade, start_rect.left)
        if w > 0:
            s = pg.transform.scale(_VSTRIP, (w, sh))
            mask.blit(s, (start_rect.left - w, 0))
    if start_rect.right < sw:
        w = min(fade, sw - start_rect.right)
        if w > 0:
            s = pg.transform.scale(_VSTRIP, (w, sh))
            s = pg.transform.flip(s, True, False)
            mask.blit(s, (start_rect.right, 0))
    if start_rect.top > 0:
        h = min(fade, start_rect.top)
        if h > 0:
            s = pg.transform.scale(_HSTRIP, (sw, h))
            mask.blit(s, (0, start_rect.top - h))
    if start_rect.bottom < sh:
        h = min(fade, sh - start_rect.bottom)
        if h > 0:
            s = pg.transform.scale(_HSTRIP, (sw, h))
            s = pg.transform.flip(s, False, True)
            mask.blit(s, (0, start_rect.bottom))

    screen.blit(mask, (0, 0))
