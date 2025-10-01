from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S


def draw_hearts(surf: pg.Surface, hp: int, max_hp: int, x: int=None, y: int=None) -> None:
    if x is None: x = S.BORDER + 2
    if y is None: y = S.BORDER + 2
    y += S.VIEW_GUTTER // 4
    for i in range(max_hp):
        pg.draw.rect(surf, (80,60,60), (x + i*30, y, 24, 24), 1)
    for i in range(hp):
        pg.draw.rect(surf, (200,80,80), (x + i*30, y, 24, 24))

def draw_hud(surf: pg.Surface, font, hp:int, max_hp: int, score: int, floor_i: int) -> None:
    draw_hearts(surf, hp, max_hp)
    txt = font.render(f"Score: {score}", True, S.WHITE)
    surf.blit(txt, (surf.get_width()-txt.get_width()-6, S.VIEW_GUTTER // 4 + 144))
    fr = font.render(f"F{floor_i+1}", True, S.GRAY)
    surf.blit(fr, (S.BORDER+2, S.VIEW_GUTTER // 4 + S.BORDER + 30))
