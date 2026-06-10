import pygame
import pygame.freetype
from settings import (
    WIDTH, HEIGHT,
    HUD_FONT_SIZE, HUD_FONT_SIZE_LARGE, HUD_FONT_SIZE_SMALL,
    HUD_BAR_WIDTH, HUD_BAR_HEIGHT, HUD_MARGIN,
    HUD_COLOR_AMMO, HUD_COLOR_RELOAD_BG, HUD_COLOR_RELOAD_FILL,
    HUD_COLOR_HP_BG, HUD_COLOR_HP_FILL,
    HUD_COLOR_XP_BG, HUD_COLOR_XP_FILL,
    HUD_COLOR_CARD_BG, HUD_COLOR_CARD_BORDER, HUD_COLOR_CARD_HOVER,
    HUD_UPGRADE_CARD_W, HUD_UPGRADE_CARD_H, HUD_UPGRADE_CARD_GAP,
)


class HUD:
    def __init__(self):
        self._font = pygame.freetype.Font(None, HUD_FONT_SIZE)
        self._font_small = pygame.freetype.Font(None, HUD_FONT_SIZE_SMALL)
        self._font_large = pygame.freetype.Font(None, HUD_FONT_SIZE_LARGE)

        _, _ref = self._font.render("A", HUD_COLOR_AMMO)
        _line_h = _ref.height

        # HP bar — top-left
        self._hp_bar_rect = pygame.Rect(
            HUD_MARGIN,
            HUD_MARGIN + _line_h + 4,
            HUD_BAR_WIDTH, HUD_BAR_HEIGHT,
        )
        self._cached_hp = -1
        self._hp_label = None

        # XP bar — below HP bar
        xp_label_y = self._hp_bar_rect.y + HUD_BAR_HEIGHT + 8
        self._xp_label_y = xp_label_y
        self._xp_bar_rect = pygame.Rect(
            HUD_MARGIN,
            xp_label_y + _line_h + 4,
            HUD_BAR_WIDTH, HUD_BAR_HEIGHT,
        )
        self._cached_level = -1
        self._xp_label = None

        # Ammo label and reload bar — bottom-left
        bar_y = HEIGHT - HUD_MARGIN - HUD_BAR_HEIGHT
        self._label_y = bar_y - _line_h - 4
        self._cached_ammo_key = None
        self._label = None
        self._bar_rect = pygame.Rect(HUD_MARGIN, bar_y, HUD_BAR_WIDTH, HUD_BAR_HEIGHT)

        # Level-up card rects (fixed positions, computed once)
        total_w = 3 * HUD_UPGRADE_CARD_W + 2 * HUD_UPGRADE_CARD_GAP
        start_x = (WIDTH - total_w) // 2
        card_y = HEIGHT // 2 - HUD_UPGRADE_CARD_H // 2 + 40
        self._card_rects = [
            pygame.Rect(start_x + i * (HUD_UPGRADE_CARD_W + HUD_UPGRADE_CARD_GAP),
                        card_y, HUD_UPGRADE_CARD_W, HUD_UPGRADE_CARD_H)
            for i in range(3)
        ]

        # Timer — top-center
        self._cached_elapsed_sec = -1
        self._timer_surf = None

        # Pre-allocated surfaces
        self._overlay_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._cached_level_up_key = None
        self._game_over_surf = None
        self._cached_game_over_elapsed = -1
        self._win_surf = None
        self._cached_win_elapsed = -1

    def _draw_bar(self, surface, bg_rect, ratio, fill_color, bg_color):
        pygame.draw.rect(surface, bg_color, bg_rect, border_radius=3)
        fill_w = int(bg_rect.width * min(1.0, max(0.0, ratio)))
        if fill_w > 0:
            fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_w, bg_rect.height)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)

    def _build_end_screen(self, title, title_color, elapsed_sec):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        title_surf, title_rect = self._font_large.render(title, title_color)
        surf.blit(title_surf, ((WIDTH - title_rect.width) // 2, HEIGHT // 2 - 100))
        m, s = divmod(elapsed_sec, 60)
        time_surf, time_rect = self._font.render(f"Time survived: {m}:{s:02d}", (200, 200, 200))
        surf.blit(time_surf, ((WIDTH - time_rect.width) // 2, HEIGHT // 2))
        hint_surf, hint_rect = self._font.render("Press R to restart", (160, 160, 160))
        surf.blit(hint_surf, ((WIDTH - hint_rect.width) // 2, HEIGHT // 2 + 44))
        return surf

    def draw(self, surface, player, elapsed=0.0):
        # Timer — top-center
        elapsed_sec = int(elapsed)
        if elapsed_sec != self._cached_elapsed_sec:
            m, s = divmod(elapsed_sec, 60)
            self._timer_surf, _ = self._font.render(f"{m}:{s:02d}", HUD_COLOR_AMMO)
            self._cached_elapsed_sec = elapsed_sec
        surface.blit(self._timer_surf, (
            (WIDTH - self._timer_surf.get_width()) // 2,
            HUD_MARGIN,
        ))

        # HP label + bar
        if player.hp != self._cached_hp:
            self._hp_label, _ = self._font.render(f"HP: {player.hp}", HUD_COLOR_AMMO)
            self._cached_hp = player.hp
        surface.blit(self._hp_label, (HUD_MARGIN, HUD_MARGIN))
        self._draw_bar(surface, self._hp_bar_rect, player.hp / player.max_hp,
                       HUD_COLOR_HP_FILL, HUD_COLOR_HP_BG)

        # XP label + bar
        if player.level != self._cached_level:
            self._xp_label, _ = self._font.render(f"LVL {player.level}", HUD_COLOR_AMMO)
            self._cached_level = player.level
        surface.blit(self._xp_label, (HUD_MARGIN, self._xp_label_y))
        xp_ratio = player.xp / player.xp_to_next if player.xp_to_next > 0 else 0.0
        self._draw_bar(surface, self._xp_bar_rect, xp_ratio, HUD_COLOR_XP_FILL, HUD_COLOR_XP_BG)

        # Ammo label + reload bar
        ammo_key = (player.ammo, player.mag_size)
        if ammo_key != self._cached_ammo_key:
            self._label, _ = self._font.render(f"{player.ammo} / {player.mag_size}", HUD_COLOR_AMMO)
            self._cached_ammo_key = ammo_key
        surface.blit(self._label, (HUD_MARGIN, self._label_y))
        reload_ratio = player.reload_progress if player.reloading else 0.0
        self._draw_bar(surface, self._bar_rect, reload_ratio,
                       HUD_COLOR_RELOAD_FILL, HUD_COLOR_RELOAD_BG)

    def hovered_upgrade(self, pos):
        """Return index (0-2) of card under pos, or -1."""
        for i, rect in enumerate(self._card_rects):
            if rect.collidepoint(pos):
                return i
        return -1

    def draw_level_up(self, surface, upgrades, mouse_pos):
        hover_idx = self.hovered_upgrade(mouse_pos)
        cache_key = (id(upgrades), hover_idx)
        if cache_key != self._cached_level_up_key:
            self._cached_level_up_key = cache_key
            self._overlay_surf.fill((0, 0, 0, 180))

            # Title
            title_surf, title_rect = self._font_large.render("LEVEL UP", (255, 220, 80))
            self._overlay_surf.blit(title_surf, (
                (WIDTH - title_rect.width) // 2,
                self._card_rects[0].y - title_rect.height - 24,
            ))

            # Cards
            for i, (rect, upgrade) in enumerate(zip(self._card_rects, upgrades)):
                hovered = i == hover_idx
                pygame.draw.rect(self._overlay_surf, HUD_COLOR_CARD_BG, rect, border_radius=8)
                border_color = HUD_COLOR_CARD_HOVER if hovered else HUD_COLOR_CARD_BORDER
                pygame.draw.rect(self._overlay_surf, border_color, rect, width=2, border_radius=8)

                key_surf, key_rect = self._font_small.render(str(i + 1), (160, 160, 200))
                self._overlay_surf.blit(key_surf, (rect.right - key_rect.width - 8, rect.y + 8))

                name_surf, name_rect = self._font.render(upgrade['name'], (220, 220, 220))
                self._overlay_surf.blit(name_surf, (rect.x + 12, rect.y + 20))

                desc_surf, _ = self._font_small.render(upgrade['desc'], (160, 160, 160))
                self._overlay_surf.blit(desc_surf, (rect.x + 12, rect.y + 20 + name_rect.height + 8))

            # Hint below cards
            hint_surf, hint_rect = self._font_small.render(
                "Press 1 / 2 / 3  or  click a card", (140, 140, 140))
            hint_y = self._card_rects[0].y + HUD_UPGRADE_CARD_H + 12
            self._overlay_surf.blit(hint_surf, ((WIDTH - hint_rect.width) // 2, hint_y))

        surface.blit(self._overlay_surf, (0, 0))

    def draw_game_over(self, surface, elapsed):
        elapsed_sec = int(elapsed)
        if self._cached_game_over_elapsed != elapsed_sec:
            self._game_over_surf = self._build_end_screen(
                "GAME OVER", (220, 60, 60), elapsed_sec)
            self._cached_game_over_elapsed = elapsed_sec
        surface.blit(self._game_over_surf, (0, 0))

    def draw_win_screen(self, surface, elapsed):
        elapsed_sec = int(elapsed)
        if self._cached_win_elapsed != elapsed_sec:
            self._win_surf = self._build_end_screen(
                "YOU SURVIVED", (220, 200, 40), elapsed_sec)
            self._cached_win_elapsed = elapsed_sec
        surface.blit(self._win_surf, (0, 0))
