from __future__ import annotations
import pygame as pg
from dataclasses import dataclass
from typing import Literal


RoomType = Literal["combat", "item", "boss"]

PATTERNS = [
    [],
    [(80,40,8,30), (232,40,8,30), (80,110,8,30), (232,110,8,30)],
    [(140,70,40,40)],
]

@dataclass
class Room:
    type: RoomType
    pattern: list[tuple[int,int,int,int]]
    
    def draw(self, surf: pg.Surface) -> None:
        surf.fill((26, 22, 32))
        pg.draw.rect(surf, (50,40,60), (0,0,*surf.get_size()), 6)
        for x,y,w,h in self.pattern:
            pg.draw.rect(surf, (60,50,70), (x,y,w,h))
