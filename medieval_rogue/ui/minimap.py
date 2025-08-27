from __future__ import annotations
import pygame as pg
from typing import Dict, Tuple
from medieval_rogue import settings as S
from medieval_rogue.dungeon.room import Room, Direction


GridPos = Tuple[int, int]

def draw_minimap(surf: pg.Surface, rooms: Dict[GridPos, Room], current: GridPos) -> None:
    if not rooms:
        return
    margin = 10
    cell = 12

    xs = [gp[0] for gp in rooms]
    ys = [gp[1] for gp in rooms]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = (maxx - minx + 1) * cell * 2
    h = (maxy - miny + 1) * cell * 2
    x0 = surf.get_width() - w - margin
    y0 = margin

    panel = pg.Rect(x0-6, y0-6, w+12, h+12)
    pg.draw.rect(surf, (20,20,26), panel)
    pg.draw.rect(surf, (60,60,80), panel, 2)

    # Connections
    for (gx, gy), r in rooms.items():
        if not S.DEBUG_MINIMAP and (not r.visited and not r.discovered):
            continue
        cx = x0 + (gx - minx) * cell * 2 + cell
        cy = y0 + (gy - miny) * cell * 2 + cell
        for side, d in r.doors.items():
            if side == "N" and (gx, gy-1) in rooms:
                pg.draw.line(surf, (80,80,110), (cx, cy), (cx, cy - cell))
            if side == "S" and (gx, gy+1) in rooms:
                pg.draw.line(surf, (80,80,110), (cx, cy), (cx, cy + cell))
            if side == "W" and (gx-1, gy) in rooms:
                pg.draw.line(surf, (80,80,110), (cx, cy), (cx - cell, cy))
            if side == "E" and (gx+1, gy) in rooms:
                pg.draw.line(surf, (80,80,110), (cx, cy), (cx + cell, cy))

    # Rooms
    for gp, r in rooms.items():
        if not S.DEBUG_MINIMAP and (not r.visited and not r.discovered):
            continue
        cx = x0 + (gp[0] - minx) * cell * 2 + cell
        cy = y0 + (gp[1] - miny) * cell * 2 + cell
        col = (70,70,90)
        if r.visited:
            col = (180,180,220) if r.kind == "start" else (140,160,220)
        elif r.discovered:
            col = (100,100,130)
        box = pg.Rect(cx - cell//2, cy - cell//2, cell, cell)
        pg.draw.rect(surf, col, box, 0 if r.visited else 2)
        if r.kind == "boss":
            pg.draw.circle(surf, (200,80,80), (cx, cy), 3)
        elif r.kind == "item":
            pg.draw.circle(surf, (220,200,120), (cx, cy), 3)

    # current room highlight
    ccx = x0 + (current[0] - minx) * cell * 2 + cell
    ccy = y0 + (current[1] - miny) * cell * 2 + cell
    pg.draw.rect(surf, (240,240,255), (ccx - cell//2 - 2, ccy - cell//2 - 2, cell + 4, cell + 4), 2)
