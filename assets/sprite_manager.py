import pygame as pg
from medieval_rogue.utils import resource_path
from typing import List, Dict, Tuple
import os

_cache = {}

def _load_image(path):
    """Load image (path can be string or list/tuple passed to resource_path). Cache result."""
    path = resource_path(*path) if isinstance(path, (list, tuple)) else resource_path(path)
    if path in _cache:
        return _cache[path]
    img = pg.image.load(path).convert_alpha()
    _cache[path] = img
    return img

def slice_sheet(img: pg.Surface, frame_w: int, frame_h: int) -> List[pg.Surface]:
    """Cut a sheet into frames; returns list of surfaces (left-to-right, top-to-bottom)."""
    frames: List[pg.Surface] = []
    w, h = img.get_width(), img.get_height()
    for y in range(0, h, frame_h):
        for x in range(0, w, frame_w):
            rect = pg.Rect(x, y, frame_w, frame_h)
            frame = pg.Surface((frame_w, frame_h), pg.SRCALPHA)
            frame.blit(img, (0, 0), rect)
            frames.append(frame)
    return frames

def load_strip(path, frame_w: int, frame_h: int) -> List[pg.Surface]:
    """Load image and slice into frames of frame_w x frame_h."""
    img = _load_image(path)
    return slice_sheet(img, frame_w, frame_h)

def flip_frames(frames: List[pg.Surface]) -> List[pg.Surface]:
    """Return horizontally flipped copies of frames."""
    return [pg.transform.flip(f, True, False) for f in frames]


class AnimatedSprite:
    """
    frames: list of surfaces (original unscaled frames).
    fps: frames per second.
    loop: whether to loop or stop at last frame.
    anchor: 'bottom' (default) or 'center' -- influences draw positioning.
    """
    def __init__(self, frames: List[pg.Surface], fps: float = 8.0, loop: bool=True, anchor: str='bottom'):
        assert frames and isinstance(frames, list)
        self.frames = frames
        self.fps = float(fps)
        self.loop = bool(loop)
        self.anchor = anchor
        self.t = 0.0
        self.idx = 0
        self.paused = False

        self._scaled_cache: Dict[int, List[pg.Surface]] = {}
        self._scaled_flipped_cache: Dict[Tuple[int,bool], List[pg.Surface]] = {}

    def update(self, dt: float):
        """dt should be seconds (clock.tick(...) / 1000.0)."""
        if self.paused or len(self.frames) <= 1:
            return
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

    def _get_scaled_frames(self, scale: int) -> List[pg.Surface]:
        """Return list of frames scaled by integer scale (cache result)."""
        if scale is None or scale <= 1:
            return self.frames
        if scale in self._scaled_cache:
            return self._scaled_cache[scale]
        scaled = []
        for f in self.frames:
            w, h = f.get_width(), f.get_height()
            sf = pg.transform.scale(f, (int(w * scale), int(h * scale)))
            scaled.append(sf)
        self._scaled_cache[scale] = scaled
        return scaled

    def _get_scaled_flipped_frames(self, scale: int, flip_x: bool) -> List[pg.Surface]:
        key = (scale, bool(flip_x))
        if key in self._scaled_flipped_cache:
            return self._scaled_flipped_cache[key]
        frames = self._get_scaled_frames(scale)
        if flip_x:
            flipped = [pg.transform.flip(f, True, False) for f in frames]
            self._scaled_flipped_cache[key] = flipped
            return flipped
        else:
            self._scaled_flipped_cache[key] = frames
            return frames

    def draw(self, surf: pg.Surface, x: float, y: float, camera=None, scale:int=1, flip_x: bool=False):
        """
        Draw the current frame to surf.
        - x,y are world coords if camera provided; otherwise screen coords.
        - scale should be an integer (1,2,3...). Non-integer scaling is not cached (but we keep integer scaling fast).
        """
        use_frames = self._get_scaled_flipped_frames(int(scale) if scale else 1, flip_x)

        frame_idx = max(0, min(self.idx, len(use_frames)-1))
        img = use_frames[frame_idx]

        w, h = img.get_width(), img.get_height()
        if camera is not None:
            sx, sy = camera.world_to_screen(x, y)
        else:
            sx, sy = int(x), int(y)

        if self.anchor == "bottom":
            blit_x = int(sx - w//2); blit_y = int(sy - h)
        else:  # center
            blit_x = int(sx - w//2); blit_y = int(sy - h//2)

        surf.blit(img, (blit_x, blit_y))
