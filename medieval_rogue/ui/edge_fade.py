from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S

EDGE_FADE_DEBUG = True

def _make_hstrip(width: int) -> pg.Surface:
    """Horizontal gradient left->right, transparent to black."""
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

    vw = pg.Rect(int(camera.x), int(camera.y), camera.w, camera.h)
    left_gap  = vw.left   - room_rect_world.left
    top_gap   = vw.top    - room_rect_world.top
    right_gap = room_rect_world.right  - vw.right
    bot_gap   = room_rect_world.bottom - vw.bottom

    def width_from_gap(gap: int) -> int:
        if gap >= fade:
            return 0
        return max(0, min(fade, fade - max(0, gap)))

    lw, tw, rw, bw = (width_from_gap(g) for g in (left_gap, top_gap, right_gap, bot_gap))

    # LEFT
    if lw > 0:
        s = pg.transform.scale(_VSTRIP, (lw, screen.get_height()))
        screen.blit(s, (0, 0))
    # RIGHT
    if rw > 0:
        s = pg.transform.scale(_VSTRIP, (rw, screen.get_height()))
        s = pg.transform.flip(s, True, False)
        screen.blit(s, (screen.get_width() - rw, 0))
    # TOP
    if tw > 0:
        s = pg.transform.scale(_HSTRIP, (screen.get_width(), tw))
        screen.blit(s, (0, 0))
    # BOTTOM
    if bw > 0:
        s = pg.transform.scale(_HSTRIP, (screen.get_width(), bw))
        s = pg.transform.flip(s, False, True)
        screen.blit(s, (0, screen.get_height() - bw))

    if EDGE_FADE_DEBUG:
        # Draw room rect projected to screen for sanity
        tl = camera.world_to_screen(room_rect_world.left, room_rect_world.top)
        br = camera.world_to_screen(room_rect_world.right, room_rect_world.bottom)
        rx = min(tl[0], br[0]); ry = min(tl[1], br[1])
        rw2 = abs(br[0] - tl[0]); rh2 = abs(br[1] - tl[1])
        pg.draw.rect(screen, (0, 255, 255), pg.Rect(rx, ry, rw2, rh2), 1)
