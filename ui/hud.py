import pygame
import pygame.freetype
from settings import (
    WIDTH, HEIGHT,
    HUD_FONT_SIZE, HUD_BAR_WIDTH, HUD_BAR_HEIGHT, HUD_MARGIN,
    HUD_COLOR_AMMO, HUD_COLOR_RELOAD_BG, HUD_COLOR_RELOAD_FILL,
    PLAYER_MAG_SIZE,
)


class HUD:
    def __init__(self):
        self._font = pygame.freetype.Font(None, HUD_FONT_SIZE)
        _, label_rect = self._font.render(f"0 / {PLAYER_MAG_SIZE}", HUD_COLOR_AMMO)
        bar_y = HEIGHT - HUD_MARGIN - HUD_BAR_HEIGHT
        self._label_y = bar_y - label_rect.height - 4
        self._cached_ammo = -1
        self._label = None
        self._bar_rect = pygame.Rect(HUD_MARGIN, bar_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT)
        self._fill_rect = pygame.Rect(HUD_MARGIN, bar_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT)

    def draw(self, surface, player):
        if player.ammo != self._cached_ammo:
            self._label, _ = self._font.render(f"{player.ammo} / {PLAYER_MAG_SIZE}", HUD_COLOR_AMMO)
            self._cached_ammo = player.ammo
        surface.blit(self._label, (HUD_MARGIN, self._label_y))

        pygame.draw.rect(surface, HUD_COLOR_RELOAD_BG, self._bar_rect, border_radius=3)

        if player.reloading:
            self._fill_rect.width = int(HUD_BAR_WIDTH * player.reload_progress)
            pygame.draw.rect(surface, HUD_COLOR_RELOAD_FILL, self._fill_rect, border_radius=3)
