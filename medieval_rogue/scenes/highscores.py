from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.save.save import load_highscores


class HighScores(Scene):
    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN and e.key in (pg.K_ESCAPE, pg.K_RETURN, pg.K_SPACE):
            self.next_scene = "menu"
    
    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()
        title = self.app.font_big.render("High Scores", True, S.YELLOW)
        surf.blit(title, (w//2 - title.get_width()//2, 20))
        scores = load_highscores()
        if not scores:
            msg = self.app.font.render("No scores yet!", True, S.GRAY)
            surf.blit(msg, (w//2 - msg.get_width()//2, h//2))
        else:
            for i, s in enumerate(scores[:10], start=1):
                row = f"{i:2d}. {s['name']:<12}  {s['score']}"
                txt = self.app.font_small.render(row, True, S.WHITE if i <= 3 else S.GRAY)
                surf.blit(txt, (w//2 - 50, 40 + i * 12))
