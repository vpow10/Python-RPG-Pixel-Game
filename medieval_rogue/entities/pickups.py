from dataclasses import dataclass
import pygame as pg
from medieval_rogue.entities.base import Entity
from medieval_rogue.items.basic_items import ITEMS


@dataclass
class ItemPickup(Entity):
    item_id: str
    w: int = 20
    h: int = 20
    
    def rect(self):
        return pg.Rect(int(self.x - self.w/2), int(self.y - self.h/2), self.w, self.h)
    
    def draw(self, surf, camera=None):
        r = self.rect()
        if camera: r = camera.world_to_screen(r.x, r.y)
        pg.draw.rect(surf, (120,80,40), r.inflate(6,6))
        pg.draw.rect(surf, (200,200,60), r)
        
    def update(self, dt, player, **kwargs):
        if player.rect().colliderect(self.rect()):
            from medieval_rogue.items.basic_items import get_item_by_name
            it = get_item_by_name(self.item_id)
            if it:
                it.apply(player)
            self.alive = False