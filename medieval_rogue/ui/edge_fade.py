from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.dungeon.room import inset_rect

EDGE_FADE_DEBUG = False

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

    wall_inner_world = inset_rect(room_rect_world, S.ROOM_INSET)
    tl = camera.world_to_screen(wall_inner_world.left, wall_inner_world.top)
    br = camera.world_to_screen(wall_inner_world.right, wall_inner_world.bottom)
    room_scr = pg.Rect(min(tl[0], br[0]), min(tl[1], br[1]),
                       abs(br[0] - tl[0]), abs(br[1] - tl[1]))
    room_scr = room_scr.clip(screen_rect)

    # LEFT band
    if room_scr.left > 0:
        w = min(fade, room_scr.left)
        if w > 0:
            s = pg.transform.scale(_VSTRIP, (w, sh))
            screen.blit(s, (room_scr.left - w, 0))

    # RIGHT band
    if room_scr.right < sw:
        w = min(fade, sw - room_scr.right)
        if w > 0:
            s = pg.transform.scale(_VSTRIP, (w, sh))
            s = pg.transform.flip(s, True, False)
            screen.blit(s, (room_scr.right, 0))

    # TOP band
    if room_scr.top > 0:
        h = min(fade, room_scr.top)
        if h > 0:
            s = pg.transform.scale(_HSTRIP, (sw, h))
            screen.blit(s, (0, room_scr.top - h))

    # BOTTOM band
    if room_scr.bottom < sh:
        h = min(fade, sh - room_scr.bottom)
        if h > 0:
            s = pg.transform.scale(_HSTRIP, (sw, h))
            s = pg.transform.flip(s, False, True)
            screen.blit(s, (0, room_scr.bottom))

    if EDGE_FADE_DEBUG:
        pg.draw.rect(screen, (0, 255, 255), room_scr, 1)
