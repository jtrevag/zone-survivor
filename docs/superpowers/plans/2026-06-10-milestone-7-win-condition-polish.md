# Milestone 7: Win Condition & Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 20-minute win condition, end screens showing time survived, screen flash on player hit, and procedurally generated sound effects for gunshot, reload, hit, and death.

**Architecture:** Win state lives in `main.py`'s game loop, checked via `WaveManager.is_complete`. End screens are built lazily in HUD with time survived baked in. Screen flash is a `hit_flash_timer` countdown on `Player`; main loop draws a translucent overlay scaled to the countdown. Sounds are generated from sine waves using Python stdlib `array` + `math` (no external audio files); `SoundManager` wraps them.

**Tech Stack:** Python 3.12, Pygame 2.x, Python stdlib `array` + `math`

---

## File Map

| File | Change |
|------|--------|
| `settings.py` | Add `WIN_TIME`, flash constants, sound constants |
| `systems/wave_manager.py` | Add `is_complete` property |
| `entities/player.py` | Add `hit_flash_timer`, `just_hit`, `reload_complete` |
| `systems/sound_manager.py` | **New** — `SoundManager` with synthetic sounds |
| `ui/hud.py` | Replace static `_game_over_surf` with lazy `draw_game_over(elapsed)`, add `draw_win_screen` |
| `main.py` | `game_won` state, flash overlay, sound calls, updated draw calls, R-key restart for both screens |
| `tests/test_win_condition.py` | **New** — `WaveManager.is_complete` tests |
| `tests/test_player_signals.py` | **New** — `hit_flash_timer`, `just_hit`, `reload_complete` tests |
| `tests/test_sound_manager.py` | **New** — `SoundManager` init + play tests |

---

## Task 1: Win condition constant + `WaveManager.is_complete`

**Files:**
- Modify: `settings.py`
- Modify: `systems/wave_manager.py`
- Create: `tests/test_win_condition.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_win_condition.py`:

```python
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWinCondition(unittest.TestCase):
    def _make(self):
        from systems.wave_manager import WaveManager
        return WaveManager()

    def test_not_complete_at_start(self):
        wm = self._make()
        self.assertFalse(wm.is_complete)

    def test_not_complete_just_before_20_minutes(self):
        wm = self._make()
        wm.update(1199.9)
        self.assertFalse(wm.is_complete)

    def test_complete_at_20_minutes(self):
        wm = self._make()
        wm.update(1200.0)
        self.assertTrue(wm.is_complete)

    def test_complete_after_20_minutes(self):
        wm = self._make()
        wm.update(1500.0)
        self.assertTrue(wm.is_complete)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_win_condition.py -v
```

Expected: `AttributeError: 'WaveManager' object has no attribute 'is_complete'`

- [ ] **Step 3: Add `WIN_TIME` to `settings.py`**

In `settings.py`, after the `WAVE_TABLE` block add:

```python
WIN_TIME = 1200.0  # 20 minutes in seconds
```

- [ ] **Step 4: Add `is_complete` to `WaveManager`**

In `systems/wave_manager.py`, change the import line from:
```python
from settings import WAVE_TABLE
```
to:
```python
from settings import WAVE_TABLE, WIN_TIME
```

Then add this property at the end of the `WaveManager` class (after the `params` property):

```python
    @property
    def is_complete(self):
        return self._elapsed >= WIN_TIME
```

- [ ] **Step 5: Run tests to verify they pass**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_win_condition.py -v
```

Expected: 4 tests PASS

- [ ] **Step 6: Run full test suite to check no regressions**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add settings.py systems/wave_manager.py tests/test_win_condition.py
git commit -m "feat: add WIN_TIME constant and WaveManager.is_complete"
```

---

## Task 2: Player signals — `hit_flash_timer`, `just_hit`, `reload_complete`

**Files:**
- Modify: `settings.py`
- Modify: `entities/player.py`
- Create: `tests/test_player_signals.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_player_signals.py`:

```python
import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()


class TestPlayerHitSignals(unittest.TestCase):
    def _make(self):
        from entities.player import Player
        return Player()

    def test_hit_flash_timer_zero_at_start(self):
        p = self._make()
        self.assertEqual(p.hit_flash_timer, 0.0)

    def test_just_hit_false_at_start(self):
        p = self._make()
        self.assertFalse(p.just_hit)

    def test_reload_complete_false_at_start(self):
        p = self._make()
        self.assertFalse(p.reload_complete)

    def test_hit_flash_timer_set_on_damage(self):
        from settings import HIT_FLASH_DURATION
        p = self._make()
        p.take_damage(10)
        self.assertAlmostEqual(p.hit_flash_timer, HIT_FLASH_DURATION)

    def test_just_hit_set_on_damage(self):
        p = self._make()
        p.take_damage(10)
        self.assertTrue(p.just_hit)

    def test_no_signal_when_already_dead(self):
        p = self._make()
        p.dead = True
        p.just_hit = False
        p.take_damage(10)
        self.assertFalse(p.just_hit)

    def test_hit_flash_timer_decrements_on_update(self):
        p = self._make()
        p.take_damage(10)
        initial = p.hit_flash_timer
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(0.05)
        self.assertLess(p.hit_flash_timer, initial)
        self.assertGreater(p.hit_flash_timer, 0.0)

    def test_reload_complete_set_when_reload_finishes(self):
        p = self._make()
        p.ammo = 0
        p.try_reload()
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(p.reload_time + 0.1)
        self.assertTrue(p.reload_complete)
        self.assertFalse(p.reloading)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_player_signals.py -v
```

Expected: `AttributeError: 'Player' object has no attribute 'hit_flash_timer'`

- [ ] **Step 3: Add flash constants to `settings.py`**

Add after the `WIN_TIME` line in `settings.py`:

```python
HIT_FLASH_DURATION = 0.15   # seconds
HIT_FLASH_COLOR = (220, 40, 40)
HIT_FLASH_ALPHA_MAX = 100   # 0–255
```

- [ ] **Step 4: Update `entities/player.py`**

Change the settings import line from:
```python
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    WHITE, INDICATOR_COLOR,
    PLAYER_SPEED, PLAYER_RADIUS, PLAYER_INDICATOR_LENGTH,
    PLAYER_MAX_HP, PLAYER_DAMAGE, PLAYER_MAG_SIZE, PLAYER_RELOAD_TIME, PLAYER_SHOT_COOLDOWN,
    XP_PER_LEVEL_BASE,
    UPGRADE_MAG_BONUS, UPGRADE_RELOAD_MULT, UPGRADE_DAMAGE_MULT,
    UPGRADE_SPEED_MULT, UPGRADE_HP_BONUS, UPGRADE_FIRE_RATE_MULT,
)
```
to:
```python
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    WHITE, INDICATOR_COLOR,
    PLAYER_SPEED, PLAYER_RADIUS, PLAYER_INDICATOR_LENGTH,
    PLAYER_MAX_HP, PLAYER_DAMAGE, PLAYER_MAG_SIZE, PLAYER_RELOAD_TIME, PLAYER_SHOT_COOLDOWN,
    XP_PER_LEVEL_BASE,
    UPGRADE_MAG_BONUS, UPGRADE_RELOAD_MULT, UPGRADE_DAMAGE_MULT,
    UPGRADE_SPEED_MULT, UPGRADE_HP_BONUS, UPGRADE_FIRE_RATE_MULT,
    HIT_FLASH_DURATION,
)
```

In `Player.__init__`, add these three lines after `self.pending_level_up = False`:

```python
        self.hit_flash_timer = 0.0
        self.just_hit = False
        self.reload_complete = False
```

In `Player.take_damage`, add two lines after `if self.dead: return`:

```python
    def take_damage(self, amount):
        if self.dead:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.dead = True
        self.hit_flash_timer = HIT_FLASH_DURATION
        self.just_hit = True
```

In `Player.update`, add timer decrement right after the shot cooldown block. Replace:

```python
        if self._shot_cooldown > 0:
            self._shot_cooldown = max(0.0, self._shot_cooldown - dt)

        if self.reloading:
            self.reload_progress = min(1.0, self.reload_progress + dt / self.reload_time)
            if self.reload_progress >= 1.0:
                self.ammo = self.mag_size
                self.reloading = False
```

with:

```python
        if self._shot_cooldown > 0:
            self._shot_cooldown = max(0.0, self._shot_cooldown - dt)

        if self.hit_flash_timer > 0:
            self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)

        if self.reloading:
            self.reload_progress = min(1.0, self.reload_progress + dt / self.reload_time)
            if self.reload_progress >= 1.0:
                self.ammo = self.mag_size
                self.reloading = False
                self.reload_complete = True
```

- [ ] **Step 5: Run tests to verify they pass**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_player_signals.py -v
```

Expected: 8 tests PASS

- [ ] **Step 6: Run full test suite**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add settings.py entities/player.py tests/test_player_signals.py
git commit -m "feat: add hit_flash_timer, just_hit, reload_complete signals to Player"
```

---

## Task 3: HUD end screens with time survived

**Files:**
- Modify: `ui/hud.py`

The current `draw_game_over` pre-builds a static surface with no time info. Replace with lazy builders that embed time survived. Add `draw_win_screen`.

- [ ] **Step 1: In `HUD.__init__`, replace the static game_over_surf build**

Replace:
```python
        # Pre-allocated surfaces
        self._overlay_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._cached_level_up_key = None
        self._game_over_surf = self._build_game_over_surf()
```
with:
```python
        # Pre-allocated surfaces
        self._overlay_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._cached_level_up_key = None
        self._game_over_surf = None
        self._cached_game_over_elapsed = -1
        self._win_surf = None
        self._cached_win_elapsed = -1
```

- [ ] **Step 2: Remove `_build_game_over_surf` and add `_build_end_screen`**

Remove the entire `_build_game_over_surf` method:
```python
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
```

Add in its place:
```python
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
```

- [ ] **Step 3: Update `draw_game_over` signature and add `draw_win_screen`**

Replace:
```python
    def draw_game_over(self, surface):
        surface.blit(self._game_over_surf, (0, 0))
```
with:
```python
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
```

- [ ] **Step 4: Verify game still launches**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python3 main.py
```

Expected: game opens. Note: `main.py` still calls `hud.draw_game_over(screen)` with no elapsed arg — it will crash when game over occurs. That's expected; main.py is fixed in Task 5.

- [ ] **Step 5: Commit**

```bash
git add ui/hud.py
git commit -m "feat: HUD end screens show time survived, add draw_win_screen"
```

---

## Task 4: Sound manager with synthetic sounds

**Files:**
- Modify: `settings.py`
- Create: `systems/sound_manager.py`
- Create: `tests/test_sound_manager.py`

Sounds are generated from sine waves at init time using Python stdlib `array` + `math`. No audio files needed.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_sound_manager.py`:

```python
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSoundManager(unittest.TestCase):
    def test_creates_exactly_four_sounds(self):
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', return_value=MagicMock()) as mock_sound:
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            self.assertEqual(mock_sound.call_count, 4)

    def test_play_gunshot_calls_play(self):
        mock_gunshot = MagicMock()
        sounds_cycle = [mock_gunshot, MagicMock(), MagicMock(), MagicMock()]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_gunshot()
            mock_gunshot.play.assert_called_once()

    def test_play_reload_calls_play(self):
        mock_reload = MagicMock()
        sounds_cycle = [MagicMock(), mock_reload, MagicMock(), MagicMock()]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_reload()
            mock_reload.play.assert_called_once()

    def test_play_hit_calls_play(self):
        mock_hit = MagicMock()
        sounds_cycle = [MagicMock(), MagicMock(), mock_hit, MagicMock()]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_hit()
            mock_hit.play.assert_called_once()

    def test_play_death_calls_play(self):
        mock_death = MagicMock()
        sounds_cycle = [MagicMock(), MagicMock(), MagicMock(), mock_death]
        with patch('pygame.mixer.pre_init'), \
             patch('pygame.mixer.Sound', side_effect=sounds_cycle):
            from systems.sound_manager import SoundManager
            sm = SoundManager()
            sm.play_death()
            mock_death.play.assert_called_once()


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_sound_manager.py -v
```

Expected: `ModuleNotFoundError: No module named 'systems.sound_manager'`

- [ ] **Step 3: Add sound constants to `settings.py`**

Add after the `HIT_FLASH_ALPHA_MAX` line:

```python
SOUND_SAMPLE_RATE = 44100
SOUND_CHANNELS = 2
SOUND_BUFFER_SIZE = 512
```

- [ ] **Step 4: Create `systems/sound_manager.py`**

```python
import array
import math
import pygame


def _make_tone(frequency, duration, volume=0.3, sample_rate=44100):
    """Sine wave with linear decay envelope, stereo 16-bit PCM."""
    n = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n):
        t = i / sample_rate
        env = max(0.0, 1.0 - t / duration)
        val = int(volume * 32767 * env * math.sin(2 * math.pi * frequency * t))
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


def _make_chirp(freq_start, freq_end, duration, volume=0.3, sample_rate=44100):
    """Linear frequency sweep, stereo 16-bit PCM."""
    n = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n):
        t = i / sample_rate
        freq = freq_start + (freq_end - freq_start) * (t / duration)
        val = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


class SoundManager:
    def __init__(self):
        from settings import SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE
        pygame.mixer.pre_init(
            frequency=SOUND_SAMPLE_RATE, size=-16,
            channels=SOUND_CHANNELS, buffer=SOUND_BUFFER_SIZE,
        )
        self._gunshot = _make_tone(800, 0.06, volume=0.5)
        self._reload = _make_chirp(200, 500, 0.2, volume=0.3)
        self._hit = _make_tone(150, 0.10, volume=0.4)
        self._death = _make_chirp(400, 80, 0.6, volume=0.5)

    def play_gunshot(self):
        self._gunshot.play()

    def play_reload(self):
        self._reload.play()

    def play_hit(self):
        self._hit.play()

    def play_death(self):
        self._death.play()
```

- [ ] **Step 5: Run tests to verify they pass**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_sound_manager.py -v
```

Expected: 5 tests PASS

- [ ] **Step 6: Run full test suite**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add settings.py systems/sound_manager.py tests/test_sound_manager.py
git commit -m "feat: add SoundManager with synthetic gunshot/reload/hit/death sounds"
```

---

## Task 5: Main loop integration

**Files:**
- Modify: `main.py`

Wire all new systems: win state, screen flash, sounds, updated HUD calls, restart from both end screens.

- [ ] **Step 1: Update imports in `main.py`**

Replace the current import block:
```python
import pygame
import random
from settings import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES
from entities.player import Player
from entities.xp_orb import XPOrb
from systems.spawner import Spawner
from systems.wave_manager import WaveManager
from ui.hud import HUD
```
with:
```python
import pygame
import random
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES,
    HIT_FLASH_COLOR, HIT_FLASH_DURATION, HIT_FLASH_ALPHA_MAX,
    SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE,
)
from entities.player import Player
from entities.xp_orb import XPOrb
from systems.spawner import Spawner
from systems.wave_manager import WaveManager
from systems.sound_manager import SoundManager
from ui.hud import HUD
```

- [ ] **Step 2: Configure mixer before `pygame.init()` and add setup in `main()`**

Replace:
```python
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    hud = HUD()

    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
    game_over = False
    level_up = False
    pending_upgrades = []
```
with:
```python
def main():
    pygame.mixer.pre_init(
        frequency=SOUND_SAMPLE_RATE, size=-16,
        channels=SOUND_CHANNELS, buffer=SOUND_BUFFER_SIZE,
    )
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    hud = HUD()
    sounds = SoundManager()

    _flash_surf = pygame.Surface((WIDTH, HEIGHT))
    _flash_surf.fill(HIT_FLASH_COLOR)

    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
    game_over = False
    game_won = False
    level_up = False
    pending_upgrades = []
```

- [ ] **Step 3: Update the event-handling block to support `game_won` restart**

Replace:
```python
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
                    game_over = False
```
with:
```python
            elif game_over or game_won:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
                    game_over = False
                    game_won = False
```

- [ ] **Step 4: Add `sounds.play_gunshot()` on fire event**

Replace:
```python
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    bullet = player.try_fire()
                    if bullet:
                        all_sprites.add(bullet)
                        bullets.add(bullet)
```
with:
```python
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    bullet = player.try_fire()
                    if bullet:
                        all_sprites.add(bullet)
                        bullets.add(bullet)
                        sounds.play_gunshot()
```

- [ ] **Step 5: Gate update on `game_won`, add win check, wire hit/reload/death sounds**

Replace:
```python
        if not game_over and not level_up:
            wave_manager.update(dt)
            wp = wave_manager.params
            all_sprites.update(dt, player)
            spawner.update(dt, all_sprites, enemies, enemy_projectiles,
                           spawn_interval=wp['spawn_interval'],
                           mutant_ratio=wp['mutant_ratio'],
                           hp_mult=wp['hp_mult'])

            hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    if enemy.take_damage(bullet.damage):
                        orb = XPOrb(enemy.pos, enemy.xp_value)
                        all_sprites.add(orb)

            for proj in pygame.sprite.spritecollide(player, enemy_projectiles, True):
                player.take_damage(proj.damage)

            if player.dead:
                game_over = True
            elif player.pending_level_up:
                player.pending_level_up = False
                level_up = True
                pending_upgrades = random.sample(UPGRADES, 3)
```
with:
```python
        if not game_over and not game_won and not level_up:
            wave_manager.update(dt)
            wp = wave_manager.params
            all_sprites.update(dt, player)
            spawner.update(dt, all_sprites, enemies, enemy_projectiles,
                           spawn_interval=wp['spawn_interval'],
                           mutant_ratio=wp['mutant_ratio'],
                           hp_mult=wp['hp_mult'])

            hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    if enemy.take_damage(bullet.damage):
                        orb = XPOrb(enemy.pos, enemy.xp_value)
                        all_sprites.add(orb)

            for proj in pygame.sprite.spritecollide(player, enemy_projectiles, True):
                player.take_damage(proj.damage)

            if player.just_hit:
                sounds.play_hit()
                player.just_hit = False
            if player.reload_complete:
                sounds.play_reload()
                player.reload_complete = False

            if player.dead:
                game_over = True
                sounds.play_death()
            elif wave_manager.is_complete:
                game_won = True
            elif player.pending_level_up:
                player.pending_level_up = False
                level_up = True
                pending_upgrades = random.sample(UPGRADES, 3)
```

- [ ] **Step 6: Update the draw section to add flash overlay and fix end-screen calls**

Replace:
```python
        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player, wave_manager.elapsed)
        if level_up:
            hud.draw_level_up(screen, pending_upgrades, pygame.mouse.get_pos())
        if game_over:
            hud.draw_game_over(screen)
        pygame.display.flip()
```
with:
```python
        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player, wave_manager.elapsed)

        if player.hit_flash_timer > 0:
            alpha = int(HIT_FLASH_ALPHA_MAX * player.hit_flash_timer / HIT_FLASH_DURATION)
            _flash_surf.set_alpha(alpha)
            screen.blit(_flash_surf, (0, 0))

        if level_up:
            hud.draw_level_up(screen, pending_upgrades, pygame.mouse.get_pos())
        if game_over:
            hud.draw_game_over(screen, wave_manager.elapsed)
        if game_won:
            hud.draw_win_screen(screen, wave_manager.elapsed)
        pygame.display.flip()
```

- [ ] **Step 7: Run full test suite**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 8: Launch the game and verify**

```
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python3 main.py
```

Verify:
- Game launches and plays normally
- Taking enemy damage triggers red screen flash
- Timer counts up in top-center HUD
- Dying shows "GAME OVER" + time survived + "Press R to restart"
- R key restarts cleanly from game over screen
- (Win screen untestable in reasonable time — verified by unit test + code review)

- [ ] **Step 9: Commit**

```bash
git add main.py
git commit -m "feat: milestone 7 — win condition, screen flash, sounds, updated end screens"
```

---

## Self-Review

### Spec coverage

| Requirement | Task |
|-------------|------|
| 20-minute survival timer on HUD | Timer already displayed; `WIN_TIME=1200` + `is_complete` added in Task 1 |
| Win screen on timer completion | Task 5 `game_won` state + Task 3 `draw_win_screen` |
| Death screen shows time survived | Task 3 `draw_game_over(elapsed)` |
| Restart works cleanly from both screens | Task 5 Step 3 |
| Basic sound effects (gunshot, reload, hit, death) | Tasks 4 + 5 |
| Screen flash on player hit | Tasks 2 + 5 |

All requirements covered. ✓

### Type / signature consistency

- `hud.draw_game_over(screen)` in old `main.py` → updated to `hud.draw_game_over(screen, wave_manager.elapsed)` in Task 5 Step 6. ✓
- `player.just_hit` set in Task 2, read and cleared in Task 5. ✓
- `player.reload_complete` set in Task 2, read and cleared in Task 5. ✓
- `player.hit_flash_timer` set in Task 2, read in Task 5. ✓
- `WaveManager.is_complete` added in Task 1, used in Task 5. ✓
- `SoundManager` created in Task 4, instantiated and used in Task 5. ✓
