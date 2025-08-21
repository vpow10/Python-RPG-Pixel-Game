from __future__ import annotations
import pygame as pg
from .. import settings as S


def draw_hearts(surf: pg.Surface, hp: int, max_hp: int, x: int=6, y: int=6) -> None:
    for i in range(max_hp):
        pg.draw.rect(surf, (80,60,60), (x + i*10, y, 8, 8), 1)
    for i in range(hp):
        pg.draw.rect(surf, (200,80,80), (x + i*10, y, 8, 8))

def draw_hud(surf: pg.Surface, font, hp:int, max_hp: int, score: int, floor_i: int, room_i: int) -> None:
    draw_hearts(surf, hp, max_hp)
    txt = font.render(f"Score: {score}", True, S.WHITE)
    surf.blit(txt, (surf.get_width()-txt.get_width()-6, 4))
    fr = font.render(f"F{floor_i+1} R{room_i+1}", True, S.GRAY)
    surf.blit(fr, (6, 16))