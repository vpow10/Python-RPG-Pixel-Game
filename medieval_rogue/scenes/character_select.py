from __future__ import annotations
import pygame as pg
from medieval_rogue import settings as S
from medieval_rogue.scene_manager import Scene
from medieval_rogue.entities.player_classes import PLAYER_CLASSES
from assets.sprite_manager import AnimatedSprite, load_strip
from medieval_rogue.save.profile import is_unlocked


class CharacterSelect(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.options = list(PLAYER_CLASSES.values())
        self.index = 0

        self.preview_map = {}
        self.preview_frame_size = (64, 64)
        for cls in self.options:
            sprite_id = getattr(cls, "sprite_id", None) or "archer"
            try:
                frames = load_strip(['assets', 'sprites', 'player', f'{sprite_id}', 'idle.png'],
                                     self.preview_frame_size[0],
                                     self.preview_frame_size[1])
                # prefer fps from class if present, otherwise default to 2 for idle previews
                fps = getattr(cls, "sprite_fps", 2.0)
                anim = AnimatedSprite(frames, fps=fps, loop=True, anchor='bottom')
                self.preview_map[sprite_id] = anim
            except Exception as exc:
                self.preview_map[sprite_id] = None

    def handle_event(self, e: pg.event.Event) -> None:
        if e.type == pg.KEYDOWN:
            if e.key in (pg.K_LEFT, pg.K_a):
                self.index = (self.index - 1) % len(self.options)
            elif e.key in (pg.K_RIGHT, pg.K_d):
                self.index = (self.index + 1) % len(self.options)
            elif e.key in (pg.K_RETURN, pg.K_SPACE):
                hero = self.options[self.index]
                if hero.id == "knight" and not is_unlocked("knight"):
                    return
                self.app.chosen_class = hero
                self.app.continue_data = None
                self.next_scene = "run"
            elif e.key == pg.K_ESCAPE:
                self.next_scene = "menu"

    def update(self, dt: float) -> None:
        # Update the currently shown preview animation
        hero = self.options[self.index]
        sprite_id = getattr(hero, "sprite_id", "archer")
        anim = self.preview_map.get(sprite_id)
        if anim:
            anim.update(dt)

    def _draw_arrow(self, surf: pg.Surface, center_x: int, center_y: int, left: bool = True):
        size = 18
        if left:
            pts = [(center_x + size//2, center_y - size), (center_x + size//2, center_y + size), (center_x - size//2, center_y)]
        else:
            pts = [(center_x - size//2, center_y - size), (center_x - size//2, center_y + size), (center_x + size//2, center_y)]
        pg.draw.polygon(surf, S.WHITE, pts)

    def draw(self, surf: pg.Surface) -> None:
        w, h = surf.get_size()

        # nice dark backdrop panel (centered)
        panel_w, panel_h = int(w * 0.8), int(h * 0.7)
        panel_x, panel_y = (w - panel_w) // 2, (h - panel_h) // 2
        pg.draw.rect(surf, (18, 22, 28), (0, 0, w, h))  # full-screen dim background
        pg.draw.rect(surf, (28, 34, 46), (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pg.draw.rect(surf, (60, 60, 80), (panel_x + 6, panel_y + 6, panel_w - 12, panel_h - 12), border_radius=6)

        # title
        title_surf = self.app.font_big.render("Choose Your Hero", True, S.GOLD if hasattr(S, "GOLD") else S.YELLOW)
        surf.blit(title_surf, (w//2 - title_surf.get_width()//2, panel_y + 14))

        # current hero card area
        hero = self.options[self.index]
        locked = (hero.id == "knight") and (not is_unlocked("knight"))
        card_w, card_h = 480, 330
        card_x = panel_x + (panel_w - card_w) // 2
        card_y = panel_y + 64
        pg.draw.rect(surf, (36, 44, 56), (card_x, card_y, card_w, card_h), border_radius=6)

        # left / right arrow hints
        arrow_y = card_y + card_h // 2
        left_x = card_x - 40
        right_x = card_x + card_w + 40
        self._draw_arrow(surf, left_x, arrow_y, left=True)
        self._draw_arrow(surf, right_x, arrow_y, left=False)

        # small hint text beneath arrows
        hint = self.app.font_small.render("Use <- -> to switch • Enter to select", True, (200,200,200))
        surf.blit(hint, (w//2 - hint.get_width()//2, card_y + card_h + 10))

        # hero name
        name_surf = self.app.font.render(hero.name, True, S.WHITE)
        surf.blit(name_surf, (card_x + 18, card_y + 8))

        # draw stat lines
        stats_x = card_x + 18
        stats_y = card_y + 42
        line_h = self.app.font.get_linesize() + 2
        stats = [
            f"HP: {hero.hp}",
            f"Damage: {hero.damage}",
            f"Speed: {hero.speed}",
            f"Fire rate: {hero.firerate}",
            f"Proj speed: {hero.proj_speed}",
        ]
        for i, s in enumerate(stats):
            txt = self.app.font_small.render(s, True, (220,220,220))
            surf.blit(txt, (stats_x, stats_y + i * line_h))

        # description block on the right side of the card
        desc_w = 160
        desc_x = card_x + card_w - desc_w - 18
        desc_y = card_y + 8
        desc_lines = self._wrap_text(hero.description or "", self.app.font_small, desc_w)
        for i, line in enumerate(desc_lines[:6]):
            txt = self.app.font_small.render(line, True, (200,200,200))
            surf.blit(txt, (desc_x, desc_y + i * (self.app.font_small.get_linesize() + 2)))

        footer = self.app.font_small.render(f"{self.index+1} / {len(self.options)}", True, (180,180,180))
        surf.blit(footer, (card_x + card_w - footer.get_width() - 8, card_y + card_h - footer.get_height() - 8))

        preview_area_x = card_x + card_w // 2 + 100
        preview_area_y = card_y + card_h // 2 + 20

        sprite_id = getattr(hero, "sprite_id", "archer")
        anim = self.preview_map.get(sprite_id)
        if anim:
            frame_w, frame_h = self.preview_frame_size
            max_w = card_w // 2
            max_h = card_h - 40
            scale_w = max(1, min(5, max_w // frame_w))
            scale_h = max(1, min(5, max_h // frame_h))
            scale = min(scale_w, scale_h, 4)  # clamp to 4 for visuals

            draw_x = preview_area_x
            draw_y = card_y + card_h - 8  # bottom of card for 'bottom' anchor
            anim.draw(surf, draw_x, draw_y, camera=None, scale=scale, flip_x=False)
        else:
            # fallback: draw placeholder rectangle
            placeholder = self.app.font_small.render("No sprite", True, (200,200,200))
            surf.blit(placeholder, (preview_area_x - placeholder.get_width()//2, preview_area_y))
        if locked:
            overlay = pg.Surface((card_w, card_h), pg.SRCALPHA)
            overlay.fill((0,0,0,160))
            surf.blit(overlay, (card_x, card_y))
            lock_txt = self.app.font.render("LOCKED", True, (255, 80, 80))
            surf.blit(lock_txt, (card_x + card_w//2 - lock_txt.get_width()//2, card_y + card_h//2 - 20))

    def _wrap_text(self, text: str, font: pg.font.Font, max_width: int) -> list[str]:
        """Utility: simple word wrap for small blocks."""
        if not text:
            return []
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines