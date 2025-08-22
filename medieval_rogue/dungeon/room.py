from __future__ import annotations
import pygame as pg
from dataclasses import dataclass
from typing import Literal, List, Tuple
from .. import settings as S

RoomType = Literal["combat", "item", "boss"]

PATTERNS: List[List[Tuple[int,int,int,int]]] = [
    [],
    [(80,40,8,30), (232,40,8,30), (80,110,8,30), (232,110,8,30)],
    [(140,70,40,40)],
]

@dataclass
class Room:
    type: RoomType
    pattern: List[Tuple[int,int,int,int]]

    def walls(self) -> List[pg.Rect]:
        surf_w, surf_h = S.BASE_W, S.BASE_H
        border = 6
        walls: List[pg.Rect] = [
            pg.Rect(0, 0, surf_w, border),               # top
            pg.Rect(0, surf_h - border, surf_w, border), # bottom
            pg.Rect(0, 0, border, surf_h),               # left
            pg.Rect(surf_w - border, 0, border, surf_h)  # right
        ]

        for x, y, w, h in self.pattern:
            walls.append(pg.Rect(x, y, w, h))

        return walls

    def draw(self, surf: pg.Surface) -> None:
        surf.fill((26, 22, 32))
        pg.draw.rect(surf, (50,40,60), (0,0,*surf.get_size()), 6)

        for x, y, w, h in self.pattern:
            pg.draw.rect(surf, (60,50,70), (x, y, w, h))
