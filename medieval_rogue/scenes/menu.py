from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.save.run_state import has_run_save, load_run_save, clear_run_save
from medieval_rogue.save.profile import load_profile


class Menu(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        opts = []
        if has_run_save():
            opts.append(("Continue", "continue"))
        opts.extend([
            ("Start", "charselect"),
            ("Stats", "stats"),
            ("High scores", "highscores"),
            ("Quit", None),
        ])
        self.options = opts
        self.index = 0
    
    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN:
            if e.key in (pg.K_DOWN, pg.K_s): self.index = (self.index + 1) % len(self.options)
            elif e.key in (pg.K_UP, pg.K_w): self.index = (self.index - 1) % len(self.options)
            elif e.key in (pg.K_RETURN, pg.K_SPACE):
                label, target = self.options[self.index]
                if target == "continue":
                    self.app.continue_data = load_run_save()
                    self.next_scene = "run"
                elif target: self.next_scene = target
                else: self.app.running = False
    
    def update(self, dt: float) -> None: ...
    
    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()
        title = self.app.font_big.render("Medieval Rogue", True, S.YELLOW)
        surf.blit(title, (w//2 - title.get_width()//2, 50))
        for i, (label, _) in enumerate(self.options):
            color = S.WHITE if i == self.index else S.GRAY
            txt = self.app.font.render(label, True, color)
            surf.blit(txt, (w//2 - txt.get_width()//2, 120 + i * 54))