# Milestone 9 — Weapons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move weapon stats out of Player into a `WEAPONS` data dict, add `Player.equip()`, refactor `Bullet` to accept explicit visual params, and add a 4-pellet shotgun weapon definition.

**Architecture:** Weapon stats (damage, mag size, bullet params) live in `WEAPONS` dict in `settings.py`. `Player.equip(weapon_def)` applies a weapon's stats to the player and resets ammo/augments. `Bullet` accepts explicit `radius`, `color`, `shape`, `speed` params rather than pulling from settings globals. `try_fire()` returns a list of Bullets (1 for pistol, 4 for shotgun) so multi-pellet weapons work without changing the call site contract.

**Tech Stack:** Python 3.12, Pygame, unittest

---

## File Map

| Action | File | Change |
|--------|------|--------|
| Modify | `settings.py` | Add `WEAPONS` dict; remove `PLAYER_DAMAGE`, `PLAYER_MAG_SIZE`, `PLAYER_RELOAD_TIME`, `PLAYER_SHOT_COOLDOWN`, `BULLET_SPEED`, `BULLET_RADIUS`, `BULLET_COLOR` (values moved into `WEAPONS`) |
| Modify | `entities/projectile.py` | `Projectile` stores `self.radius`; `Bullet.__init__` takes explicit params; `Bullet.draw()` handles `'circle'` and `'rect'` |
| Modify | `entities/player.py` | Add `import math`; replace per-stat constants with `equip(WEAPONS['pistol'])` call in `__init__`; add `equip(weapon_def)`; `try_fire()` returns `list[Bullet]` |
| Modify | `main.py` | Update `try_fire()` call site to handle list; add Tab toggle (pistol↔shotgun, ENCOUNTER only, dev-only) |
| Modify | `ui/hud.py` | Add weapon name label above ammo counter (small font, cached on `player.weapon['name']`) |
| Modify | `docs/ENTITIES.md` | Sync Player stat table with current code values; replace "Player Bullet" entry with per-weapon bullet entries |
| Modify | `docs/MECHANICS.md` | Add Weapons section describing pistol and shotgun |
| Create | `tests/test_weapons_settings.py` | Verify WEAPONS dict structure |
| Create | `tests/test_bullet.py` | Verify Bullet draws circle and rect without error |
| Create | `tests/test_player_equip.py` | Verify equip() and try_fire() behavior |

---

## Task 1: Add WEAPONS dict to settings.py

**Files:**
- Modify: `settings.py`
- Create: `tests/test_weapons_settings.py`

### Step 1.1 — Write the failing test

```python
# tests/test_weapons_settings.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest


class TestWeaponsSettings(unittest.TestCase):
    def test_weapons_dict_exists(self):
        from settings import WEAPONS
        self.assertIsInstance(WEAPONS, dict)

    def test_pistol_exists(self):
        from settings import WEAPONS
        self.assertIn('pistol', WEAPONS)

    def test_shotgun_exists(self):
        from settings import WEAPONS
        self.assertIn('shotgun', WEAPONS)

    def test_each_weapon_has_required_keys(self):
        from settings import WEAPONS
        required = {'name', 'damage', 'mag_size', 'reload_time', 'shot_cooldown', 'pellets', 'spread', 'bullet'}
        for name, wdef in WEAPONS.items():
            with self.subTest(weapon=name):
                self.assertTrue(required.issubset(wdef.keys()))

    def test_each_bullet_def_has_required_keys(self):
        from settings import WEAPONS
        required = {'speed', 'radius', 'color', 'shape'}
        for name, wdef in WEAPONS.items():
            with self.subTest(weapon=name):
                self.assertTrue(required.issubset(wdef['bullet'].keys()))

    def test_pistol_pellets(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['pistol']['pellets'], 1)

    def test_shotgun_pellets(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['shotgun']['pellets'], 4)

    def test_shotgun_spread(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['shotgun']['spread'], 25.0)

    def test_shotgun_mag_size(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['shotgun']['mag_size'], 2)


if __name__ == '__main__':
    unittest.main()
```

### Step 1.2 — Run test to verify it fails

```bash
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_weapons_settings.py -v
```

Expected: FAIL with `ImportError: cannot import name 'WEAPONS'`

### Step 1.3 — Add WEAPONS dict to settings.py

In `settings.py`, after the existing `# Player` block and before `# Mutant`, replace the four weapon-specific player constants and the three bullet constants with a `WEAPONS` dict. The existing `PLAYER_SPEED`, `PLAYER_RADIUS`, `PLAYER_INDICATOR_LENGTH`, `PLAYER_MAX_HP` stay — they are not weapon stats.

Remove these lines from `settings.py`:
```python
PLAYER_DAMAGE = 55
PLAYER_MAG_SIZE = 6
PLAYER_RELOAD_TIME = 1.2  # seconds
PLAYER_SHOT_COOLDOWN = 0.4  # seconds
```

And later:
```python
BULLET_SPEED = 500        # px/s
BULLET_RADIUS = 4
BULLET_COLOR = (255, 255, 0)  # yellow
```

Replace the removed player weapon lines with:
```python
# Weapons — each entry is a complete weapon definition
WEAPONS = {
    'pistol': {
        'name': 'Pistol',
        'damage': 55,
        'mag_size': 6,
        'reload_time': 1.2,
        'shot_cooldown': 0.4,
        'pellets': 1,
        'spread': 0.0,
        'bullet': {
            'speed': 500,
            'radius': 4,
            'color': (255, 255, 0),
            'shape': 'circle',
        },
    },
    'shotgun': {
        'name': 'Shotgun',
        'damage': 20,
        'mag_size': 2,
        'reload_time': 1.8,
        'shot_cooldown': 0.6,
        'pellets': 4,
        'spread': 25.0,
        'bullet': {
            'speed': 500,
            'radius': 4,
            'color': (255, 165, 0),
            'shape': 'circle',
        },
    },
}
```

### Step 1.4 — Run test to verify it passes

```bash
python -m pytest tests/test_weapons_settings.py -v
```

Expected: 9 PASS

### Step 1.5 — Commit

```bash
git add settings.py tests/test_weapons_settings.py
git commit -m "feat: add WEAPONS dict to settings — pistol and shotgun definitions"
```

---

## Task 2: Refactor Bullet to accept explicit params

**Files:**
- Modify: `entities/projectile.py`
- Create: `tests/test_bullet.py`

### Step 2.1 — Write the failing test

```python
# tests/test_bullet.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest


def _make_bullet(shape='circle', radius=4, color=(255, 255, 0), speed=500, damage=55):
    from entities.projectile import Bullet
    direction = pygame.math.Vector2(1, 0)
    return Bullet((100, 100), direction, damage, radius, color, shape, speed)


class TestBullet(unittest.TestCase):
    def test_bullet_stores_radius(self):
        b = _make_bullet(radius=4)
        self.assertEqual(b.radius, 4)

    def test_bullet_stores_color(self):
        b = _make_bullet(color=(255, 0, 0))
        self.assertEqual(b.color, (255, 0, 0))

    def test_bullet_stores_shape(self):
        b = _make_bullet(shape='rect')
        self.assertEqual(b.shape, 'rect')

    def test_bullet_stores_damage(self):
        b = _make_bullet(damage=30)
        self.assertEqual(b.damage, 30)

    def test_circle_draw_does_not_raise(self):
        b = _make_bullet(shape='circle')
        surf = pygame.Surface((200, 200))
        b.draw(surf)

    def test_rect_draw_does_not_raise(self):
        b = _make_bullet(shape='rect')
        surf = pygame.Surface((200, 200))
        b.draw(surf)

    def test_bullet_rect_size_matches_radius(self):
        b = _make_bullet(radius=6)
        self.assertEqual(b.rect.width, 12)
        self.assertEqual(b.rect.height, 12)

    def test_bullet_velocity_direction(self):
        direction = pygame.math.Vector2(0, 1)
        from entities.projectile import Bullet
        b = Bullet((0, 0), direction, 55, 4, (255, 255, 0), 'circle', 300)
        self.assertAlmostEqual(b.vel.x, 0.0)
        self.assertAlmostEqual(b.vel.y, 300.0)


if __name__ == '__main__':
    unittest.main()
```

### Step 2.2 — Run test to verify it fails

```bash
python -m pytest tests/test_bullet.py -v
```

Expected: FAIL — `TypeError` (Bullet constructor doesn't accept the new params yet)

### Step 2.3 — Refactor projectile.py

Replace the entire contents of `entities/projectile.py` with:

```python
import math
import pygame
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    BANDIT_PROJECTILE_SPEED, BANDIT_PROJECTILE_RADIUS,
    BANDIT_PROJECTILE_COLOR, BANDIT_PROJECTILE_DAMAGE,
)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed, radius, damage):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.vel = direction * speed
        self.damage = damage
        self.radius = radius
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, player=None):
        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if (self.pos.x < ARENA_LEFT or self.pos.x > ARENA_RIGHT or
                self.pos.y < ARENA_TOP or self.pos.y > ARENA_BOTTOM):
            self.kill()


class Bullet(Projectile):
    def __init__(self, pos, direction, damage, radius, color, shape, speed):
        super().__init__(pos, direction, speed, radius, damage)
        self.color = color
        self.shape = shape

    def draw(self, surface):
        if self.shape == 'circle':
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius)
        elif self.shape == 'rect':
            cx, cy = self.rect.center
            angle = math.atan2(self.vel.y, self.vel.x)
            hl = self.radius * 2
            hw = max(1, self.radius // 2)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            pts = [
                (cx + cos_a * hl - sin_a * hw, cy + sin_a * hl + cos_a * hw),
                (cx + cos_a * hl + sin_a * hw, cy + sin_a * hl - cos_a * hw),
                (cx - cos_a * hl + sin_a * hw, cy - sin_a * hl - cos_a * hw),
                (cx - cos_a * hl - sin_a * hw, cy - sin_a * hl + cos_a * hw),
            ]
            pygame.draw.polygon(surface, self.color, pts)


class BanditProjectile(Projectile):
    def __init__(self, pos, direction):
        super().__init__(pos, direction, BANDIT_PROJECTILE_SPEED, BANDIT_PROJECTILE_RADIUS, BANDIT_PROJECTILE_DAMAGE)

    def draw(self, surface):
        pygame.draw.circle(surface, BANDIT_PROJECTILE_COLOR, self.rect.center, self.radius)
```

Note: `BanditProjectile.draw()` now uses `self.radius` instead of the imported constant — same value, but cleaner.

### Step 2.4 — Run test to verify it passes

```bash
python -m pytest tests/test_bullet.py -v
```

Expected: 8 PASS

### Step 2.5 — Verify existing tests still pass

```bash
python -m pytest tests/ -v
```

Expected: all existing tests PASS (Bullet constructor change only affects player.py which we haven't updated yet — existing test_player_signals.py does not call try_fire(), so it won't be broken yet)

### Step 2.6 — Commit

```bash
git add entities/projectile.py tests/test_bullet.py
git commit -m "feat: refactor Bullet to accept explicit radius/color/shape/speed params"
```

---

## Task 3: Add Player.equip() and refactor try_fire()

**Files:**
- Modify: `entities/player.py`
- Create: `tests/test_player_equip.py`

### Step 3.1 — Write the failing test

```python
# tests/test_player_equip.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import math
import unittest
from unittest.mock import patch
from settings import WEAPONS


def _player():
    from entities.player import Player
    return Player()


class TestPlayerEquip(unittest.TestCase):
    def test_player_starts_with_pistol(self):
        p = _player()
        self.assertEqual(p.weapon, WEAPONS['pistol'])

    def test_player_has_augments_list(self):
        p = _player()
        self.assertEqual(p.augments, [])

    def test_equip_sets_mag_size(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.mag_size, WEAPONS['shotgun']['mag_size'])

    def test_equip_sets_reload_time(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertAlmostEqual(p.reload_time, WEAPONS['shotgun']['reload_time'])

    def test_equip_sets_shot_cooldown(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertAlmostEqual(p.shot_cooldown_base, WEAPONS['shotgun']['shot_cooldown'])

    def test_equip_sets_damage(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.damage, WEAPONS['shotgun']['damage'])

    def test_equip_resets_ammo_to_mag_size(self):
        p = _player()
        p.ammo = 0
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.ammo, WEAPONS['shotgun']['mag_size'])

    def test_equip_clears_augments(self):
        p = _player()
        p.augments = ['fake_augment']
        p.equip(WEAPONS['pistol'])
        self.assertEqual(p.augments, [])

    def test_try_fire_returns_list(self):
        p = _player()
        result = p.try_fire()
        self.assertIsInstance(result, list)

    def test_pistol_fires_one_bullet(self):
        p = _player()
        bullets = p.try_fire()
        self.assertEqual(len(bullets), 1)

    def test_shotgun_fires_four_bullets(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        p.facing.update(1, 0)
        bullets = p.try_fire()
        self.assertEqual(len(bullets), 4)

    def test_shotgun_spread_is_25_degrees(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        p.facing.update(1, 0)
        bullets = p.try_fire()
        angles = [math.degrees(math.atan2(b.vel.y, b.vel.x)) for b in bullets]
        spread = max(angles) - min(angles)
        self.assertAlmostEqual(spread, 25.0, places=3)

    def test_try_fire_empty_when_no_ammo(self):
        p = _player()
        p.ammo = 0
        self.assertEqual(p.try_fire(), [])

    def test_try_fire_empty_when_reloading(self):
        p = _player()
        p.reloading = True
        self.assertEqual(p.try_fire(), [])

    def test_try_fire_decrements_ammo(self):
        p = _player()
        before = p.ammo
        p.try_fire()
        self.assertEqual(p.ammo, before - 1)

    def test_reload_still_works_after_equip_refactor(self):
        p = _player()
        p.ammo = 0
        p.try_reload()
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(p.reload_time + 0.1)
        self.assertTrue(p.reload_complete)
        self.assertEqual(p.ammo, p.mag_size)


if __name__ == '__main__':
    unittest.main()
```

### Step 3.2 — Run test to verify it fails

```bash
python -m pytest tests/test_player_equip.py -v
```

Expected: FAIL — `AttributeError: 'Player' object has no attribute 'weapon'` (and similar)

### Step 3.3 — Refactor player.py

Replace the entire contents of `entities/player.py` with:

```python
import math
import pygame
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    WHITE, INDICATOR_COLOR,
    PLAYER_SPEED, PLAYER_RADIUS, PLAYER_INDICATOR_LENGTH,
    PLAYER_MAX_HP,
    WEAPONS,
    XP_PER_LEVEL_BASE,
    UPGRADE_MAG_BONUS, UPGRADE_RELOAD_MULT, UPGRADE_DAMAGE_MULT,
    UPGRADE_SPEED_MULT, UPGRADE_HP_BONUS, UPGRADE_FIRE_RATE_MULT,
    HIT_FLASH_DURATION,
)
from entities.projectile import Bullet


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(
            (ARENA_LEFT + ARENA_RIGHT) / 2,
            (ARENA_TOP + ARENA_BOTTOM) / 2,
        )
        self.facing = pygame.math.Vector2(1, 0)
        self._move = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.dead = False

        self.move_speed = PLAYER_SPEED

        self.reloading = False
        self.reload_progress = 0.0
        self._shot_cooldown = 0.0

        # XP / leveling
        self.xp = 0
        self.level = 1
        self.xp_to_next = XP_PER_LEVEL_BASE
        self.pending_level_up = False

        self.hit_flash_timer = 0.0
        self.just_hit = False
        self.reload_complete = False

        self.augments = []
        self.equip(WEAPONS['pistol'])

    def equip(self, weapon_def):
        # TODO M10: replay self._upgrades_taken after equip so upgrades persist across weapon swaps
        self.weapon = weapon_def
        self.mag_size = weapon_def['mag_size']
        self.reload_time = weapon_def['reload_time']
        self.shot_cooldown_base = weapon_def['shot_cooldown']
        self.damage = weapon_def['damage']
        self.ammo = self.mag_size
        self.augments = []

    def take_damage(self, amount):
        if self.dead:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.dead = True
        else:
            self.just_hit = True
        self.hit_flash_timer = HIT_FLASH_DURATION

    def collect_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = XP_PER_LEVEL_BASE * self.level
            self.pending_level_up = True

    def apply_upgrade(self, upgrade_id):
        if upgrade_id == 'mag':
            self.mag_size += UPGRADE_MAG_BONUS
            self.ammo = min(self.ammo + UPGRADE_MAG_BONUS, self.mag_size)
        elif upgrade_id == 'reload':
            self.reload_time *= UPGRADE_RELOAD_MULT
        elif upgrade_id == 'damage':
            self.damage = int(self.damage * UPGRADE_DAMAGE_MULT)
        elif upgrade_id == 'speed':
            self.move_speed *= UPGRADE_SPEED_MULT
        elif upgrade_id == 'hp':
            self.max_hp += UPGRADE_HP_BONUS
            self.hp = min(self.hp + UPGRADE_HP_BONUS, self.max_hp)
        elif upgrade_id == 'fire_rate':
            self.shot_cooldown_base *= UPGRADE_FIRE_RATE_MULT

    def try_fire(self):
        """Return list of Bullets; empty list means cannot fire."""
        if self.reloading or self._shot_cooldown > 0 or self.ammo <= 0:
            return []
        self.ammo -= 1
        self._shot_cooldown = self.shot_cooldown_base

        weapon = self.weapon
        pellets = weapon['pellets']
        spread = weapon['spread']
        bdef = weapon['bullet']

        if pellets == 1 or spread == 0.0:
            directions = [pygame.math.Vector2(self.facing)]
        else:
            base_angle = math.degrees(math.atan2(self.facing.y, self.facing.x))
            half = spread / 2.0
            step = spread / (pellets - 1)
            directions = [
                pygame.math.Vector2(
                    math.cos(math.radians(base_angle - half + step * i)),
                    math.sin(math.radians(base_angle - half + step * i)),
                )
                for i in range(pellets)
            ]

        return [
            Bullet(self.pos, d, weapon['damage'], bdef['radius'], bdef['color'], bdef['shape'], bdef['speed'])
            for d in directions
        ]

    def try_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_progress = 0.0

    def update(self, dt, player=None):
        keys = pygame.key.get_pressed()
        self._move.update(keys[pygame.K_d] - keys[pygame.K_a],
                          keys[pygame.K_s] - keys[pygame.K_w])
        if self._move.length_squared() > 0:
            self._move.normalize_ip()
            self.pos += self._move * self.move_speed * dt

        self.pos.x = max(ARENA_LEFT + PLAYER_RADIUS, min(ARENA_RIGHT - PLAYER_RADIUS, self.pos.x))
        self.pos.y = max(ARENA_TOP + PLAYER_RADIUS, min(ARENA_BOTTOM - PLAYER_RADIUS, self.pos.y))

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        to_mouse = pygame.math.Vector2(pygame.mouse.get_pos()) - self.pos
        if to_mouse.length_squared() > 0:
            to_mouse.normalize_ip()
            self.facing.update(to_mouse)

        if self._shot_cooldown > 0:
            self._shot_cooldown = max(0.0, self._shot_cooldown - dt)

        if self.reloading:
            self.reload_progress = min(1.0, self.reload_progress + dt / self.reload_time)
            if self.reload_progress >= 1.0:
                self.ammo = self.mag_size
                self.reloading = False
                self.reload_complete = True

    def draw(self, surface):
        center = self.rect.center
        pygame.draw.circle(surface, WHITE, center, PLAYER_RADIUS)
        tip = pygame.math.Vector2(center) + self.facing * PLAYER_INDICATOR_LENGTH
        pygame.draw.line(surface, INDICATOR_COLOR, center, tip, 2)
```

### Step 3.4 — Run test to verify it passes

```bash
python -m pytest tests/test_player_equip.py -v
```

Expected: 16 PASS

### Step 3.5 — Run full test suite

```bash
python -m pytest tests/ -v
```

Expected: all tests PASS (including pre-existing test_player_signals.py — `p.reload_time` is still set by `equip()`)

### Step 3.6 — Commit

```bash
git add entities/player.py tests/test_player_equip.py
git commit -m "feat: add Player.equip() and refactor try_fire() to return list"
```

---

## Task 4: Update main.py — call site + Tab dev toggle

**Files:**
- Modify: `main.py`

### Step 4.1 — Update try_fire() call site and add Tab toggle

In `main.py`, make two changes:

**Change 1** — find the `MOUSEBUTTONDOWN` handler that calls `player.try_fire()`. Replace:

```python
bullet = player.try_fire()
if bullet:
    all_sprites.add(bullet)
    bullets.add(bullet)
    sounds.play_gunshot()
```

With:

```python
fired = player.try_fire()
if fired:
    for bullet in fired:
        all_sprites.add(bullet)
        bullets.add(bullet)
    sounds.play_gunshot()
```

**Change 2** — add `WEAPONS` to the imports at the top of `main.py`:

```python
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES,
    HIT_FLASH_COLOR, HIT_FLASH_DURATION, HIT_FLASH_ALPHA_MAX,
    SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE,
    ROOM_SEQUENCE, WEAPONS,
)
```

**Change 3** — in the `else:` branch of the event handler (the branch that handles normal ENCOUNTER input — where `K_r` and `MOUSEBUTTONDOWN` are handled), add a Tab toggle after the existing keybinds:

```python
# DEV ONLY — remove in M10 when reward screen handles weapon equip
elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
    if player.weapon is WEAPONS['pistol']:
        player.equip(WEAPONS['shotgun'])
    else:
        player.equip(WEAPONS['pistol'])
    print(f"[DEV] weapon: {player.weapon['name']}")
```

The `else:` branch already has the guard `run_manager.state not in ('WIN', 'GAME_OVER', 'REWARD')` and `not level_up`, so Tab naturally only fires during ENCOUNTER when not paused.

### Step 4.2 — Run full test suite

```bash
python -m pytest tests/ -v
```

Expected: all PASS

### Step 4.3 — Launch and smoke-test

```bash
source .venv/bin/activate && python3 main.py
```

Verify:
- Game loads, player circle renders
- Left-click fires a single yellow bullet (pistol, ammo shows 6/6)
- R key reloads as before
- Tab switches to shotgun (console prints `[DEV] weapon: Shotgun`, ammo shows 2/2)
- Left-click fires 4 orange bullets in a spread cone
- Tab switches back to pistol
- Enemies and collisions work normally

### Step 4.4 — Commit

```bash
git add main.py
git commit -m "feat: update try_fire() call site to handle list; add dev Tab weapon toggle"
```

---

## Task 5: HUD weapon name display

**Files:**
- Modify: `ui/hud.py`

### Step 5.1 — Add weapon name label above ammo counter

In `ui/hud.py`, make the following changes:

**In `__init__`**, after the existing ammo label setup block (after `self._bar_rect = ...`), add:

```python
# Weapon name label — above ammo counter
self._weapon_label_y = self._label_y - _line_h - 4
self._cached_weapon_name = None
self._weapon_label = None
```

**In `draw()`**, after the ammo label block (after the `self._draw_bar(...)` call for the reload bar), add:

```python
# Weapon name
weapon_name = player.weapon['name']
if weapon_name != self._cached_weapon_name:
    self._weapon_label, _ = self._font_small.render(weapon_name, (160, 160, 160))
    self._cached_weapon_name = weapon_name
surface.blit(self._weapon_label, (HUD_MARGIN, self._weapon_label_y))
```

### Step 5.2 — Launch and verify HUD layout

```bash
source .venv/bin/activate && python3 main.py
```

Verify:
- "Pistol" appears in bottom-left above the ammo counter in small dim text
- Tab toggle changes it to "Shotgun" immediately
- No overlap with ammo counter or reload bar

### Step 5.3 — Commit

```bash
git add ui/hud.py
git commit -m "feat: show active weapon name in HUD bottom-left"
```

---

## Task 6: Update docs

**Files:**
- Modify: `docs/ENTITIES.md`
- Modify: `docs/MECHANICS.md`

### Step 6.1 — Sync ENTITIES.md Player table and add weapon entries

The current `docs/ENTITIES.md` Player table is out of sync with the code. Update the Player section and replace the "Player Bullet" section.

In `docs/ENTITIES.md`, replace the Player property table:

```markdown
| Property | Value |
|----------|-------|
| move_speed | 200 px/s |
| max_hp | 100 |
| hp | 100 |
| mag_size | 5 |
| ammo | 5 |
| reload_time | 2.0s |
| is_reloading | false |
| reload_progress | 0.0–1.0 |
| damage | 40 |
| shot_cooldown | 0.4s |
```

With:

```markdown
| Property | Value |
|----------|-------|
| move_speed | 200 px/s |
| max_hp | 100 |
| hp | 100 |
| weapon | pistol (default) |
| mag_size | set by equipped weapon |
| ammo | set by equipped weapon |
| reload_time | set by equipped weapon |
| is_reloading | false |
| reload_progress | 0.0–1.0 |
| damage | set by equipped weapon |
| shot_cooldown | set by equipped weapon |
| augments | [] (empty at start) |
```

Replace the "### Player Bullet" section with:

```markdown
### Pistol Bullet
**Placeholder:** Yellow circle, radius 4px

| Property | Value |
|----------|-------|
| speed | 500 px/s |
| damage | 55 (player.damage) |
| pellets | 1 |
| spread | 0° |
| shape | circle |
| lifetime | until hit or out of bounds |

### Shotgun Pellet
**Placeholder:** Orange circle, radius 4px

| Property | Value |
|----------|-------|
| speed | 500 px/s |
| damage | 20 per pellet (×4 pellets) |
| pellets | 4 |
| spread | 25° cone |
| shape | circle |
| lifetime | until hit or out of bounds |
```

### Step 6.2 — Add Weapons section to MECHANICS.md

In `docs/MECHANICS.md`, after the `## Reload System` section, add:

```markdown
---

## Weapons

Weapons are defined as data in `WEAPONS` dict in `settings.py`. Equipping a weapon sets the player's mag size, reload time, shot cooldown, damage, and bullet params. Augments clear on weapon swap (applied in Milestone 10).

### Pistol (default)
- 6-round mag, 1.2s reload, 0.4s shot cooldown
- Fires 1 bullet per shot
- Damage: 55

### Shotgun
- 2-round mag, 1.8s reload, 0.6s shot cooldown
- Fires 4 pellets per shot in a 25° spread cone
- Damage: 20 per pellet (up to 80 total at point-blank)
```

### Step 6.3 — Commit

```bash
git add docs/ENTITIES.md docs/MECHANICS.md
git commit -m "docs: sync ENTITIES.md with current stats; document pistol and shotgun"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| Weapons as data — move weapon stats out of Player into WEAPONS dict (settings.py) | Task 1 |
| Player.equip(weapon_def) — sets self.weapon, resets ammo, clears augments | Task 3 |
| Shotgun weapon definition — 2-shot mag, 4 pellets, 25° spread cone | Task 1 |
| Bullet accepts radius, shape, color; draw() handles "circle" and "rect" | Task 2 |

All four spec requirements covered, plus two additions from design session: Tab dev toggle (Task 4) and HUD weapon name (Task 5). ✓

**Placeholder scan:** No TBDs, no "implement later", no "similar to Task N". ✓

**Type consistency:**
- `try_fire()` returns `list[Bullet]` — `main.py` iterates over it ✓
- `Bullet(pos, direction, damage, radius, color, shape, speed)` — all call sites pass all params ✓
- `equip(weapon_def)` accesses `weapon_def['pellets']`, `weapon_def['spread']`, `weapon_def['bullet']` — all keys defined in Task 1 ✓
- `BanditProjectile.draw()` uses `self.radius` — added to `Projectile` base in Task 2 ✓
- `player.weapon['name']` used in HUD Task 5 — `'name'` key present in all WEAPONS entries (Task 1) ✓
