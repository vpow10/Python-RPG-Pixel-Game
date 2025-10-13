from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.save.profile import load_profile


class Stats(Scene):
    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN and e.key in (pg.K_ESCAPE, pg.K_RETURN):
            self.next_scene = "menu"
        
    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()
        title = self.app.font_big.render("Stats", True, S.YELLOW)
        surf.blit(title, (w//2 - title.get_width()//2, 50))
        
        p = load_profile()
        stats = p["stats"]
        rows = [
            ("Runs started", stats["runs_started"]),
            ("Runs won", stats["runs_won"]),
            ("Bosses defeated", stats["bosses_defeated"]),
            ("Rooms cleared", stats["rooms_cleared"]),
            ("Archer wins", stats["archer_wins"]),
        ]
        
        y = 140
        for label, val in rows:
            txt = self.app.font_small.render(f"{label}: {val}", True, S.WHITE)
            surf.blit(txt, (w//2 - 200, y))
            y += 40
