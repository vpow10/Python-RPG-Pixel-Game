from __future__ import annotations
import pygame as pg
import random
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import SceneManager
from medieval_rogue.scenes.menu import Menu
from medieval_rogue.scenes.character_select import CharacterSelect
from medieval_rogue.scenes.run import RunScene
from medieval_rogue.scenes.game_over import GameOver
from medieval_rogue.scenes.highscores import HighScores
import medieval_rogue.entities


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
    app.font = pg.font.Font(None, 48)
    app.font_big = pg.font.Font(None, 72)
    app.font_small = pg.font.Font(None, 42)
    
    
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
        if S.SMOOTH_SCALE:
            scaled = pg.transform.smoothscale(screen, window.get_size())
        else:
            scaled = pg.transform.scale(screen, window.get_size())
        window.blit(scaled, (0, 0))
        pg.display.flip()
