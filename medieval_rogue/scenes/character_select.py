from __future__ import annotations
import pygame as pg
from .. import settings as S
from ..scene_manager import Scene


ARCHER_STATS = {
    "name": "Archer",
    "hp": S.PLAYER_BASE_HP,
    "speed": S.PLAYER_BASE_SPEED,
    "firerate": S.PLAYER_BASE_FIRERATE,
    "proj_speed": S.PLAYER_BASE_PROJ_SPEED,
    "damage": S.PLAYER_BASE_DAMAGE,
}


class CharacterSelect(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.options = [ARCHER_STATS]
        self.index = 0
        
    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN:
            if e.key in (pg.K_LEFT, pg.K_a, pg.K_RIGHT, pg.K_d):
                self.index = (self.index + 1) % len(self.options)
            elif e.key in (pg.K_RETURN, pg.K_SPACE):
                self.app.chosen_stats = self.options[self.index]
                self.next_scene = "run"
            elif e.key == pg.K_ESCAPE:
                self.next_scene = "menu"
        
    def update(self, dt: float) -> None: ...
    
    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()
        title = self.app.font_big.render("Choose Your Hero", True, S.YELLOW)
        surf.blit(title, (w//2 - title.get_width()//2, 20))
        hero = self.options[self.index]
        card_w, card_h = 140, 90
        card_x, card_y = w//2 - card_w//2, h//2 - card_h//2
        pg.draw.rect(surf, (40,40,60), (card_x, card_y, card_w, card_h))
        name = self.app.font.render(hero["name"], True, S.WHITE)
        surf.blit(name, (w//2 - name.get_width()//2, card_y + 6))