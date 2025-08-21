from __future__ import annotations
import pygame as pg
import random
from . import settings as S
from .scene_manager import SceneManager
from .scenes.menu import Menu
from .scenes.character_select import CharacterSelect
from .scenes.run import RunScene
from .scenes.game_over import GameOver
from .scenes.highscores import HighScores



def run() -> None:
    pg.init()
    pg.display.set_caption("Medieval Rogue")
    window = pg.display.set_mode((S.BASE_W * S.SCALE, S.BASE_H * S.SCALE))
    clock = pg.time.Clock()
    
    # Low-res render target for crisp pixels
    screen = pg.Surface((S.BASE_W, S.BASE_H))
    
    random.seed(S.RANDOM_SEED)
    
    class App: pass
    app = App()
    app.window = window
    app.screen = screen
    app.clock = clock
    app.running = True
    app.font = pg.font.Font(None, 16)
    app.font_big = pg.font.Font(None, 24)
    
    
    sm = SceneManager(app)
    sm.register("menu", Menu)
    sm.register("charselect", CharacterSelect)
    sm.register("run", RunScene)
    sm.register("gameover", GameOver)
    sm.register("highscores", HighScores)
    sm.switch("menu")
    
    while app.running:
        dt = clock.tick(S.FPS) / 1000.0
        for e in pg.event.get():
            if e.type == pg.QUIT: app.running = False
            sm.handle_event(e)
        sm.update(dt)
        screen.fill((24, 20, 28))
        sm.draw(screen)
        pg.transform.scale(screen, window.get_size(), window)
        pg.display.flip()
