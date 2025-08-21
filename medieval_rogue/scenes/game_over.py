from __future__ import annotations
import pygame as pg
from .. import settings as S
from ..scene_manager import Scene


# Placeholder for now
class GameOver(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        
    def update(self, dt: float) -> None: ...
    
    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()
        title = self.app.font_big.render("Game Over", True, S.RED)
        surf.blit(title, (w//2 - title.get_width()//2, 30))