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
    UPGRADES,
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

        # Weapon name label — above ammo counter
        self._weapon_label_y = self._label_y - _line_h - 4
        self._cached_weapon_name = None
        self._weapon_label = None

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
        self._cached_timer_text = None
        self._timer_surf = None

        # Pre-allocated surfaces
        self._overlay_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._cached_level_up_key = None
        self._game_over_surf = None
        self._cached_game_over_elapsed = -1
        self._win_surf = None
        self._cached_win_elapsed = -1
        self._room_clear_surf = None

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

    def draw(self, surface, player, room=None):
        # Timer — top-center (text supplied by room; None hides it)
        if room is not None and room.timer_display is not None:
            timer_text = room.timer_display
            if timer_text != self._cached_timer_text:
                self._timer_surf, _ = self._font.render(timer_text, HUD_COLOR_AMMO)
                self._cached_timer_text = timer_text
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
        ammo_key = (player.ammo, player.effective_mag_size())
        if ammo_key != self._cached_ammo_key:
            self._label, _ = self._font.render(f"{player.ammo} / {player.effective_mag_size()}", HUD_COLOR_AMMO)
            self._cached_ammo_key = ammo_key
        surface.blit(self._label, (HUD_MARGIN, self._label_y))
        reload_ratio = player.reload_progress if player.reloading else 0.0
        self._draw_bar(surface, self._bar_rect, reload_ratio,
                       HUD_COLOR_RELOAD_FILL, HUD_COLOR_RELOAD_BG)

        # Weapon name
        weapon_name = player.weapon['name']
        if weapon_name != self._cached_weapon_name:
            self._weapon_label, _ = self._font_small.render(weapon_name, (160, 160, 160))
            self._cached_weapon_name = weapon_name
        surface.blit(self._weapon_label, (HUD_MARGIN, self._weapon_label_y))

        # Augment slot squares — 2 slots always shown, filled = augment color, empty = outline
        sq_x = HUD_MARGIN + self._weapon_label.get_width() + 6
        sq_y = self._weapon_label_y + (self._weapon_label.get_height() - 10) // 2
        for i in range(2):
            sq_rect = pygame.Rect(sq_x + i * 14, sq_y, 10, 10)
            if i < len(player.augments):
                pygame.draw.rect(surface, player.augments[i]['color'], sq_rect)
            else:
                pygame.draw.rect(surface, (60, 60, 60), sq_rect, 1)

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

    def draw_reward(self, surface, player, cards, mouse_pos):
        hover_idx = self.hovered_upgrade(mouse_pos)
        augments_full = len(player.augments) >= 2

        self._overlay_surf.fill((0, 0, 0, 180))

        title_surf, title_rect = self._font_large.render('ROOM CLEAR', (220, 220, 220))
        self._overlay_surf.blit(title_surf, (
            (WIDTH - title_rect.width) // 2,
            self._card_rects[0].y - title_rect.height - 24,
        ))

        for i, (rect, card) in enumerate(zip(self._card_rects, cards)):
            hovered = i == hover_idx
            is_full = card['type'] == 'augment' and augments_full

            bg_color = HUD_COLOR_CARD_BG
            border_color = (80, 60, 60) if is_full else (HUD_COLOR_CARD_HOVER if hovered else HUD_COLOR_CARD_BORDER)
            pygame.draw.rect(self._overlay_surf, bg_color, rect, border_radius=8)
            pygame.draw.rect(self._overlay_surf, border_color, rect, width=2, border_radius=8)

            key_surf, key_rect = self._font_small.render(str(i + 1), (160, 160, 200))
            self._overlay_surf.blit(key_surf, (rect.right - key_rect.width - 8, rect.y + 8))

            if card['type'] == 'weapon':
                wdef = card['weapon_def']
                name_surf, name_rect = self._font.render(
                    f"SWAP → {wdef['name']}", (220, 220, 220))
                self._overlay_surf.blit(name_surf, (rect.x + 12, rect.y + 20))

                stats = (f"DMG {wdef['damage']}  "
                         f"MAG {wdef['mag_size']}  "
                         f"RLD {wdef['reload_time']:.1f}s")
                stats_surf, _ = self._font_small.render(stats, (160, 160, 160))
                self._overlay_surf.blit(stats_surf, (rect.x + 12, rect.y + 20 + name_rect.height + 8))

                reset_surf, _ = self._font_small.render('Augments reset', (180, 80, 80))
                self._overlay_surf.blit(reset_surf, (rect.x + 12, rect.bottom - 28))

                carry_surf, _ = self._font_small.render('Upgrades carry over', (100, 130, 100))
                self._overlay_surf.blit(carry_surf, (rect.x + 12, rect.bottom - 14))

            else:
                adef = card['augment_def']
                name_color = (120, 120, 120) if is_full else (220, 220, 220)
                name_surf, name_rect = self._font.render(adef['name'], name_color)
                self._overlay_surf.blit(name_surf, (rect.x + 12, rect.y + 20))

                desc_surf, _ = self._font_small.render(adef['desc'], (160, 160, 160))
                self._overlay_surf.blit(desc_surf, (rect.x + 12, rect.y + 20 + name_rect.height + 8))

                if is_full:
                    full_surf, _ = self._font_small.render('FULL', (180, 80, 80))
                    self._overlay_surf.blit(full_surf, (rect.x + 12, rect.bottom - 22))
                else:
                    attach_text = f"Attaches to {player.weapon['name']}"
                    attach_surf, _ = self._font_small.render(attach_text, (100, 100, 130))
                    self._overlay_surf.blit(attach_surf, (rect.x + 12, rect.bottom - 22))

        hint_surf, hint_rect = self._font_small.render(
            'Press 1 / 2 / 3  or  click a card', (140, 140, 140))
        hint_y = self._card_rects[0].y + HUD_UPGRADE_CARD_H + 12
        self._overlay_surf.blit(hint_surf, ((WIDTH - hint_rect.width) // 2, hint_y))

        surface.blit(self._overlay_surf, (0, 0))

    def draw_pause(self, surface, player):
        from collections import Counter
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))

        title_surf, title_rect = self._font_large.render('PAUSED', (220, 220, 220))
        overlay.blit(title_surf, ((WIDTH - title_rect.width) // 2, 60))

        col_y = 160
        col_left = WIDTH // 2 - 260
        col_right = WIDTH // 2 + 40

        head_surf, _ = self._font.render('UPGRADES', (200, 200, 100))
        overlay.blit(head_surf, (col_left, col_y))

        upgrade_name_map = {u['id']: u['name'] for u in UPGRADES}
        counts = Counter(player._upgrade_history)
        if counts:
            for row, (uid, n) in enumerate(counts.items()):
                label = upgrade_name_map.get(uid, uid)
                text = f"{label} ×{n}" if n > 1 else label
                line_surf, _ = self._font_small.render(text, (180, 180, 180))
                overlay.blit(line_surf, (col_left, col_y + 36 + row * 24))
        else:
            none_surf, _ = self._font_small.render('None yet', (120, 120, 120))
            overlay.blit(none_surf, (col_left, col_y + 36))

        whead_surf, _ = self._font.render('WEAPON', (200, 200, 100))
        overlay.blit(whead_surf, (col_right, col_y))

        wname_surf, wname_rect = self._font.render(player.weapon['name'], (220, 220, 220))
        overlay.blit(wname_surf, (col_right, col_y + 36))

        if player.augments:
            for row, aug in enumerate(player.augments):
                aug_surf, _ = self._font_small.render(f"  • {aug['name']}", (180, 180, 180))
                overlay.blit(aug_surf, (col_right, col_y + 36 + wname_rect.height + 8 + row * 22))
        else:
            na_surf, _ = self._font_small.render('  No augments', (120, 120, 120))
            overlay.blit(na_surf, (col_right, col_y + 36 + wname_rect.height + 8))

        footer_surf, footer_rect = self._font_small.render(
            'ESC  resume        Q  quit', (140, 140, 140))
        overlay.blit(footer_surf, ((WIDTH - footer_rect.width) // 2, HEIGHT - 50))

        surface.blit(overlay, (0, 0))

    def draw_room_clear(self, surface):
        if self._room_clear_surf is None:
            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 160))
            title_surf, title_rect = self._font_large.render('ROOM CLEAR', (220, 220, 220))
            surf.blit(title_surf, (
                (WIDTH - title_rect.width) // 2,
                HEIGHT // 2 - 60,
            ))
            sub_surf, sub_rect = self._font.render('Press SPACE to continue', (160, 160, 160))
            surf.blit(sub_surf, (
                (WIDTH - sub_rect.width) // 2,
                HEIGHT // 2 + 10,
            ))
            self._room_clear_surf = surf
        surface.blit(self._room_clear_surf, (0, 0))
