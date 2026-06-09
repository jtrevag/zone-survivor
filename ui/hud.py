import pygame
import pygame.freetype
from settings import (
    WIDTH, HEIGHT,
    HUD_FONT_SIZE, HUD_FONT_SIZE_LARGE,
    HUD_BAR_WIDTH, HUD_BAR_HEIGHT, HUD_MARGIN,
    HUD_COLOR_AMMO, HUD_COLOR_RELOAD_BG, HUD_COLOR_RELOAD_FILL,
    HUD_COLOR_HP_BG, HUD_COLOR_HP_FILL,
    PLAYER_MAG_SIZE,
)


class HUD:
    def __init__(self):
        self._font = pygame.freetype.Font(None, HUD_FONT_SIZE)
        self._font_large = pygame.freetype.Font(None, HUD_FONT_SIZE_LARGE)

        # HP bar — top-left
        _, hp_label_rect = self._font.render("HP: 100", HUD_COLOR_AMMO)
        self._hp_bar_rect = pygame.Rect(
            HUD_MARGIN,
            HUD_MARGIN + hp_label_rect.height + 4,
            HUD_BAR_WIDTH, HUD_BAR_HEIGHT,
        )
        self._cached_hp = -1
        self._hp_label = None

        # Ammo label and reload bar — bottom-left
        _, ammo_label_rect = self._font.render(f"0 / {PLAYER_MAG_SIZE}", HUD_COLOR_AMMO)
        bar_y = HEIGHT - HUD_MARGIN - HUD_BAR_HEIGHT
        self._label_y = bar_y - ammo_label_rect.height - 4
        self._cached_ammo = -1
        self._label = None
        self._bar_rect = pygame.Rect(HUD_MARGIN, bar_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT)

        # Game-over overlay — pre-built once, blit whole surface each call
        self._game_over_surf = self._build_game_over_surf()

    def _build_game_over_surf(self):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        go_surf, go_rect = self._font_large.render("GAME OVER", (220, 60, 60))
        surf.blit(go_surf, (
            (WIDTH - go_rect.width) // 2,
            HEIGHT // 2 - go_rect.height - 16,
        ))
        sub_surf, sub_rect = self._font.render("Press R to restart", (200, 200, 200))
        surf.blit(sub_surf, (
            (WIDTH - sub_rect.width) // 2,
            HEIGHT // 2 + 16,
        ))
        return surf

    def _draw_bar(self, surface, bg_rect, ratio, fill_color, bg_color):
        pygame.draw.rect(surface, bg_color, bg_rect, border_radius=3)
        fill_w = int(bg_rect.width * min(1.0, max(0.0, ratio)))
        if fill_w > 0:
            fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_w, bg_rect.height)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)

    def draw(self, surface, player):
        # HP label + bar
        if player.hp != self._cached_hp:
            self._hp_label, _ = self._font.render(f"HP: {player.hp}", HUD_COLOR_AMMO)
            self._cached_hp = player.hp
        surface.blit(self._hp_label, (HUD_MARGIN, HUD_MARGIN))
        self._draw_bar(surface, self._hp_bar_rect, player.hp / player.max_hp,
                       HUD_COLOR_HP_FILL, HUD_COLOR_HP_BG)

        # Ammo label + reload bar
        if player.ammo != self._cached_ammo:
            self._label, _ = self._font.render(f"{player.ammo} / {PLAYER_MAG_SIZE}", HUD_COLOR_AMMO)
            self._cached_ammo = player.ammo
        surface.blit(self._label, (HUD_MARGIN, self._label_y))
        reload_ratio = player.reload_progress if player.reloading else 0.0
        self._draw_bar(surface, self._bar_rect, reload_ratio,
                       HUD_COLOR_RELOAD_FILL, HUD_COLOR_RELOAD_BG)

    def draw_game_over(self, surface):
        surface.blit(self._game_over_surf, (0, 0))
