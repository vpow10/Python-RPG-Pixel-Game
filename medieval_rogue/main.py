from __future__ import annotations
import pygame as pg
import random
from . import settings as S


def run() -> None:
    pg.init()
    pg.display.set_caption("Medieval Rogue")
    window = pg.display.set_mode((S.BASE_W * S.SCALE, S.BASE_H * S.SCALE))
    clock = pg.time.Clock()
    
    # Low-res render target for crisp pixels
    screen = pg.Surface((S.BASE_W, S.BASE_H))
    
    random.seed(S.RANDOM_SEED)
    
    running = True
    while running:
        dt = clock.tick(S.FPS) / 1000.0
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
                
        # temporary background
        screen.fill((24, 20, 28))
        
        # scale up to window
        pg.transform.scale(screen, window.get_size(), window)
        pg.display.flip()
    
    pg.quit()