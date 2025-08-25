from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.save.save import save_highscore


# Placeholder for now
class GameOver(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.saved = False
        self.name = "YOU"

    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN:
            if not self.saved and e.unicode and e.key not in (pg.K_RETURN, pg.K_ESCAPE, pg.K_BACKSPACE):
                if len(self.name) < 16 and e.unicode.isprintable():
                    self.name += e.unicode.upper()
            if e.key == pg.K_BACKSPACE and len(self.name) > 0:
                self.name = self.name[:-1]
            if e.key == pg.K_RETURN:
                if not self.saved:
                    save_highscore(self.name, self.app.final_score)
                    self.saved = True
                    self.next_scene = "menu"
                if e.key == pg.K_r: self.next_scene = "run"
                if e.key == pg.K_ESCAPE: self.next_scene = "menu"
        
    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()
        title = self.app.font_big.render("Game Over", True, S.RED)
        surf.blit(title, (w//2 - title.get_width()//2, 72))
        score = self.app.font.render(f"Score: {self.app.final_score}", True, S.WHITE)
        surf.blit(score, (w//2 - score.get_width()//2, 180))
        name = self.app.font.render(f"Name: {self.name}", True, S.YELLOW)
        surf.blit(name, (w//2 - name.get_width()//2, 234))
