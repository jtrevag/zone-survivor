# Milestone 9 Post-Playtest Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix three playtest issues: weapon swap resets ammo (should persist), upgrades lost on weapon swap (should replay), player has no recovery between rooms (should heal 25% on room start).

**Architecture:** Task 1 refactors `Player.equip()` — adds per-weapon ammo dict and an upgrade history list that gets replayed after base stats reset. Task 2 adds `Player.heal(fraction)` and wires it into `main.py` after `run_manager.advance()`. Both tasks follow TDD. No new files needed.

**Tech Stack:** Python 3.12, Pygame, unittest

---

## File Map

| Action | File | Change |
|--------|------|--------|
| Modify | `settings.py` | Add `ROOM_HEAL_FRACTION = 0.25` |
| Modify | `entities/player.py` | Add `_WEAPON_UPGRADE_IDS` constant; add `_ammo_by_weapon` dict and `_upgrade_history` list in `__init__`; refactor `equip()` to save/restore ammo and replay upgrades; split `apply_upgrade()` into public tracker + private `_apply_one_upgrade()`; add `heal(fraction)` |
| Modify | `main.py` | Import `ROOM_HEAL_FRACTION`; call `player.heal(ROOM_HEAL_FRACTION)` after `run_manager.advance()` when new state is `'ENCOUNTER'` |
| Modify | `tests/test_player_equip.py` | Add 7 new tests covering ammo persistence, upgrade replay, and heal |
| Modify | `docs/MECHANICS.md` | Add room-start heal note to Weapons section |

---

## Task 1: Per-weapon ammo + upgrade persistence in Player.equip()

**Files:**
- Modify: `entities/player.py`
- Modify: `tests/test_player_equip.py`

### Step 1.1 — Write failing tests

Add these 5 tests to the bottom of `TestPlayerEquip` in `tests/test_player_equip.py`:

```python
def test_ammo_persists_after_weapon_swap(self):
    p = _player()
    p.try_fire()  # pistol: 5/6 ammo
    ammo_before = p.ammo
    p.equip(WEAPONS['shotgun'])
    p.equip(WEAPONS['pistol'])
    self.assertEqual(p.ammo, ammo_before)

def test_damage_upgrade_persists_after_weapon_swap(self):
    p = _player()
    p.apply_upgrade('damage')
    expected_damage = p.damage
    p.equip(WEAPONS['shotgun'])
    p.equip(WEAPONS['pistol'])
    self.assertEqual(p.damage, expected_damage)

def test_mag_upgrade_persists_after_weapon_swap(self):
    p = _player()
    p.apply_upgrade('mag')
    expected_mag = p.mag_size
    p.equip(WEAPONS['shotgun'])
    p.equip(WEAPONS['pistol'])
    self.assertEqual(p.mag_size, expected_mag)

def test_reload_upgrade_persists_after_weapon_swap(self):
    p = _player()
    p.apply_upgrade('reload')
    expected_reload = p.reload_time
    p.equip(WEAPONS['shotgun'])
    p.equip(WEAPONS['pistol'])
    self.assertAlmostEqual(p.reload_time, expected_reload)

def test_speed_upgrade_not_reset_by_equip(self):
    p = _player()
    p.apply_upgrade('speed')
    expected_speed = p.move_speed
    p.equip(WEAPONS['shotgun'])
    self.assertAlmostEqual(p.move_speed, expected_speed)
```

### Step 1.2 — Run tests to verify they fail

```bash
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_player_equip.py -v -k "persists or speed_upgrade"
```

Expected: 5 FAIL — damage/reload/mag reset to weapon defaults after swap.

### Step 1.3 — Refactor entities/player.py

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

# Upgrade IDs that scale with the active weapon and must be replayed after equip.
# 'speed' and 'hp' are player-wide and never reset, so they are excluded.
_WEAPON_UPGRADE_IDS = frozenset({'mag', 'reload', 'damage', 'fire_rate'})


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

        self._ammo_by_weapon = {}   # weapon name → saved ammo
        self._upgrade_history = []  # ordered list of applied upgrade IDs
        self.equip(WEAPONS['pistol'])

    def equip(self, weapon_def):
        # Persist current weapon's ammo before switching
        if hasattr(self, 'weapon'):
            self._ammo_by_weapon[self.weapon['name']] = self.ammo

        self.weapon = weapon_def
        self.mag_size = weapon_def['mag_size']
        self.reload_time = weapon_def['reload_time']
        self.shot_cooldown_base = weapon_def['shot_cooldown']
        self.damage = weapon_def['damage']
        self.reloading = False
        self.reload_progress = 0.0
        self.augments = []

        # Replay weapon-specific upgrades on top of the new weapon's base stats
        for uid in self._upgrade_history:
            if uid in _WEAPON_UPGRADE_IDS:
                self._apply_one_upgrade(uid)

        # Restore saved ammo (or full mag if first equip), clamped to current mag_size
        self.ammo = min(
            self._ammo_by_weapon.get(weapon_def['name'], self.mag_size),
            self.mag_size,
        )

    def heal(self, fraction):
        self.hp = min(self.max_hp, self.hp + int(self.max_hp * fraction))

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
        self._upgrade_history.append(upgrade_id)
        self._apply_one_upgrade(upgrade_id)

    def _apply_one_upgrade(self, upgrade_id):
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
            Bullet(self.pos, d, self.damage, bdef['radius'], bdef['color'], bdef['shape'], bdef['speed'])
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

### Step 1.4 — Run new tests

```bash
python -m pytest tests/test_player_equip.py -v -k "persists or speed_upgrade"
```

Expected: 5 PASS

### Step 1.5 — Run full suite

```bash
python -m pytest tests/ -v
```

Expected: all 93 tests PASS.

### Step 1.6 — Commit

```bash
git add entities/player.py tests/test_player_equip.py
git commit -m "feat: persist ammo and replay upgrades across weapon swaps"
```

---

## Task 2: Room-start heal

**Files:**
- Modify: `settings.py`
- Modify: `main.py`
- Modify: `tests/test_player_equip.py`
- Modify: `docs/MECHANICS.md`

Note: `Player.heal(fraction)` is already added in Task 1 Step 1.3. If running Task 2 standalone, add it to `entities/player.py`:
```python
def heal(self, fraction):
    self.hp = min(self.max_hp, self.hp + int(self.max_hp * fraction))
```

### Step 2.1 — Write failing tests

Add these 2 tests to `TestPlayerEquip` in `tests/test_player_equip.py`:

```python
def test_heal_restores_hp(self):
    p = _player()
    p.take_damage(50)
    hp_before = p.hp
    p.heal(0.25)
    self.assertEqual(p.hp, hp_before + int(p.max_hp * 0.25))

def test_heal_clamps_to_max_hp(self):
    p = _player()
    p.heal(1.0)
    self.assertEqual(p.hp, p.max_hp)
```

### Step 2.2 — Run tests to verify they fail

```bash
python -m pytest tests/test_player_equip.py -v -k "heal"
```

Expected: 2 FAIL — `AttributeError: 'Player' object has no attribute 'heal'`

### Step 2.3 — Add ROOM_HEAL_FRACTION to settings.py

In `settings.py`, after `PLAYER_MAX_HP = 100`, add:

```python
ROOM_HEAL_FRACTION = 0.25   # fraction of max_hp restored on room start
```

### Step 2.4 — Run heal tests

```bash
python -m pytest tests/test_player_equip.py -v -k "heal"
```

Expected: 2 PASS (heal() was added in Task 1; settings constant now exists).

### Step 2.5 — Wire heal into main.py

Update the settings import at the top of `main.py`:

```python
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES,
    HIT_FLASH_COLOR, HIT_FLASH_DURATION, HIT_FLASH_ALPHA_MAX,
    SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE,
    ROOM_SEQUENCE, WEAPONS, ROOM_HEAL_FRACTION,
)
```

In the `REWARD` state event handler, replace the existing `run_manager.advance()` call:

```python
elif run_manager.state == 'REWARD':
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        for e in list(enemies):
            e.kill()
        for p in list(enemy_projectiles):
            p.kill()
        for o in list(xp_orbs):
            o.kill()
        run_manager.advance()
        if run_manager.state == 'ENCOUNTER':
            player.heal(ROOM_HEAL_FRACTION)
```

### Step 2.6 — Run full suite

```bash
python -m pytest tests/ -v
```

Expected: all 95 tests PASS.

### Step 2.7 — Update docs/MECHANICS.md

In `docs/MECHANICS.md`, inside the `## Weapons` section after the Shotgun entry, add:

```markdown
### Room Transitions
On advancing to the next room the player heals `ROOM_HEAL_FRACTION` (25%) of their max HP. Rewards room clears while keeping accumulated damage meaningful.
```

### Step 2.8 — Commit

```bash
git add settings.py main.py tests/test_player_equip.py docs/MECHANICS.md
git commit -m "feat: heal 25% max HP on room start"
```
