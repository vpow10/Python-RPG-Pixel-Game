from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S

# Build a 1D horizontal/vertical alpha gradient strip once and reuse.

def _make_strip(length: int) -> pg.Surface:
    surf = pg.Surface((length, 1), pg.SRCALPHA)
    arr = pg.PixelArray(surf)
    for x in range(length):
        a = int(255 * (x / max(1, length-1)))
        arr[x,0] = (0 << 24) | (0 << 16) | (0 << 8) | a
    del arr
    return pg.transform.smoothscale(surf, (length, 1))

_HSTRIP = _make_strip(S.EDGE_FADE)
_VSTRIP = pg.transform.rotate(_HSTRIP, 90)


def draw_edge_fade(screen: pg.Surface, camera, room_rect_world: pg.Rect) -> None:
    fade = int(S.EDGE_FADE)
    if fade <= 0:
        return
    vw = pg.Rect(int(camera.x), int(camera.y), camera.w, camera.h)

    left_gap = (vw.left - room_rect_world.left)
    top_gap = (vw.top - room_rect_world.top)
    right_gap = (room_rect_world.right - vw.right)
    bot_gap = (room_rect_world.bottom - vw.bottom)

    # Helper to compute fade width (0..fade) for each side
    def w(d):
        if d >= fade: return 0 # fully inside, no fade
        return max(0, min(fade, fade - max(0, d)))


    lw, tw, rw, bw = w(left_gap), w(top_gap), w(right_gap), w(bot_gap)


    # Left
    if lw > 0:
        strip = pg.transform.scale(_VSTRIP, (lw, screen.get_height()))
        screen.blit(strip, (0, 0))
    # Right
    if rw > 0:
        strip = pg.transform.scale(_VSTRIP, (rw, screen.get_height()))
        strip = pg.transform.flip(strip, True, False)
        screen.blit(strip, (screen.get_width() - rw, 0))
    # Top
    if tw > 0:
        strip = pg.transform.scale(_HSTRIP, (screen.get_width(), tw))
        screen.blit(strip, (0, 0))
    # Bottom
    if bw > 0:
        strip = pg.transform.scale(_HSTRIP, (screen.get_width(), bw))
        strip = pg.transform.flip(strip, False, True)
        screen.blit(strip, (0, screen.get_height() - bw))