import pygame as pg
from medieval_rogue.utils import resource_path
from medieval_rogue import settings as S
from typing import List, Tuple
import os


_cache = {}

def _load_image(path):
    path = resource_path(*path) if isinstance(path, (list, tuple)) else resource_path(path)
    if path in _cache:
        return _cache[path]
    img = pg.image.load(path).convert_alpha()
    _cache[path] = img
    return img

def slice_sheet(img: pg.Surface, frame_w: int, frame_h: int) -> List[pg.Surface]:
    sheets = []
    w, h = img.get_width(), img.get_height()
    for y in range(0, h, frame_h):
        for x in range(0, w, frame_w):
            rect = pg.Rect(x, y, frame_w, frame_h)
            frame = pg.Surface((frame_w, frame_h), pg.SRCALPHA)
            frame.blit(img, (0, 0), rect)
            sheets.append(frame)
    return sheets

def load_strip(path, frame_w: int, frame_h: int) -> List[pg.Surface]:
    img = _load_image(path)
    return slice_sheet(img, frame_w, frame_h)

def flip_frames(frames: List[pg.Surface]) -> List[pg.Surface]:
    return [pg.transform.flip(f, True, False) for f in frames]

class AnimatedSprite:
    def __init__(self, frames: List[pg.Surface], fps: float = 8.0, loop: bool=True, anchor: str='bottom'):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.anchor = anchor
        self.t = 0.0
        self.idx = 0
        self.paused = False

    def update(self, dt: float):
        if self.paused or len(self.frames) <= 1: return
        self.t += dt
        step = 1.0 / max(1e-6, self.fps)
        while self.t >= step:
            self.t -= step
            self.idx += 1
            if self.idx >= len(self.frames):
                if self.loop:
                    self.idx = 0
                else:
                    self.idx = len(self.frames) - 1
                    self.paused = True

    def current(self) -> pg.Surface:
        return self.frames[self.idx]

    def draw(self, surf: pg.Surface, x: float, y: float, camera=None, scale:int=1, flip_x: bool=False):
        img = self.current()
        if flip_x:
            img = pg.transform.flip(img, True, False)
        w, h = img.get_width(), img.get_height()
        if camera is not None:
            sx, sy = camera.world_to_screen(x, y)
        else:
            sx, sy = int(x), int(y)
        if self.anchor == "bottom":
            blit_x = int(sx - w//2); blit_y = int(sy - h)
        else:
            blit_x = int(sx - w//2); blit_y = int(sy - h//2)
        surf.blit(img, (blit_x, blit_y))
