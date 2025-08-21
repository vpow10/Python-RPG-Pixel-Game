from __future__ import annotations
import pygame as pg
from typing import Optional, Dict, Type


class Scene:
    def __init__(self, app: 'App') -> None:
        self.app = app
        self.next_scene: Optional[str] = None
        
    def handle_event(self, e: pg.event.Event) -> None: ...
    
    def update(self, dt: float) -> None: ...
    
    def draw(self, surf: pg.Surface) -> None: ...
    
    
class SceneManager:
    def __init__(self, app: 'App') -> None:
        self.app = app
        self.scenes: Dict[str, Type[Scene]] = {}
        self.current: Optional[Scene] = None
        
    def register(self, name: str, cls: Type[Scene]) -> None:
        self.scenes[name] = cls
        
    def switch(self, name: str) -> None:
        self.current = self.scenes[name](self.app)
        
    def handle_event(self, e: pg.event.Event) -> None:
        if self.current: self.current.handle_event(e)
        
    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)
            if self.current.next_scene:
                self.switch(self.current.next_scene)
                
    def draw(self, surf: pg.Surface) -> None:
        if self.current: self.current.draw(surf)
