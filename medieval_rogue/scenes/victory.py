from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.save.save import save_highscore
from medieval_rogue.save.profile import record_run_finished
from medieval_rogue.save.run_state import clear_run_save


class Victory(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.saved = False
        self.name = "YOU"
        
    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_RETURN:
                if not self.saved:
                    save_highscore(self.name, self.app.final_score)
                    self.saved = True
                    self.next_scene = "menu"
            elif e.key == pg.K_r:
                self.next_scene = "run"
            elif e.key == pg.K_ESCAPE:
                self.next_scene = "menu"
            elif e.key == pg.K_BACKSPACE:
                self.name = self.name[:-1]
            else:
                ch = e.unicode
                if ch and (ch.isalnum() or ch in ("_", "-", " ")):
                    if len(self.name) < 12:
                        self.name = (self.name + ch.upper()) 
                        
    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()
        title = self.app.font_big.render("Victory!", True, S.GREEN)
        surf.blit(title, (w//2 - title.get_width()//2, 72))
        
        score = self.app.font.render(f"Score: {self.app.final_score}", True, S.WHITE)
        surf.blit(score, (w//2 - score.get_width()//2, 180))

        name = self.app.font.render(f"Name: {self.name}", True, S.YELLOW)
        surf.blit(name, (w//2 - name.get_width()//2, 234))

        hint1 = self.app.font_small.render("Enter = save & menu", True, S.GRAY)
        surf.blit(hint1, (w//2 - hint1.get_width()//2, 300))
        hint2 = self.app.font_small.render("R = restart run • ESC = menu", True, S.GRAY)
        surf.blit(hint2, (w//2 - hint2.get_width()//2, 340))