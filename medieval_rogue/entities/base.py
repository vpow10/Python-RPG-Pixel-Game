from __future__ import annotations
import pygame as pg
from dataclasses import dataclass


@dataclass
class Entity:
    x: float
    y: float
    alive: bool = True

    def rect(self) -> pg.Rect:
        raise NotImplementedError

    def update(self, dt: float, **kwargs) -> None:
        raise NotImplementedError

    def draw(self, surf: pg.Surface, camera=None) -> None:
        raise NotImplementedError

    def center(self) -> pg.Vector2:
        r = self.rect()
        return pg.Vector2(r.centerx, r.centery)
