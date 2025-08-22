from __future__ import annotations
import pygame as pg
from typing import Iterable, Tuple


def move_and_collide(
        x: float,
        y: float,
        w: int,
        h: int,
        dx: float,
        dy: float,
        walls: Iterable[pg.Rect],
        ox: int = 0,
        oy: int = 0,
        stop_on_collision: bool = False,
) -> Tuple[float, float, bool]:
    """
    Move an entity from (x,y) by (dx,dy). The entity's collision rect is
    at (x+ox, y+oy) with size (w,h).

    Returns: (new_x, new_y, collided)
      - collided is True if a collision was detected and stop_on_collision=True
        (useful for projectiles).
      - If stop_on_collision is False, movement is clamped against walls.
    """
    collided = False

    cx = x + dx
    rect_h = pg.Rect(int(round(cx + ox)), int(round(y + oy)), w, h)
    for wall in walls:
        if rect_h.colliderect(wall):
            collided = True
            if stop_on_collision:
                cx = x
            else:
                if dx > 0:
                    cx = wall.left - ox - w
                elif dx < 0:
                    cx = wall.right - ox
            rect_h.x = int(round(cx + ox))
    cy = y + dy
    rect_v = pg.Rect(int(round(cx + ox)), int(round(cy + oy)), w, h)
    for wall in walls:
        if rect_v.colliderect(wall):
            collided = True
            if stop_on_collision:
                cy = y
            else:
                if dy > 0:
                    cy = wall.top - oy - h
                elif dy < 0:
                    cy = wall.bottom - oy
            rect_v.y = int(round(cy + oy))

    return cx, cy, collided