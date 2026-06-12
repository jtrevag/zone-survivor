# Milestone 10 — Augments & Room Rewards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add weapon-specific augments awarded at room-clear reward screens, with pierce mechanics, pause screen, and laser pointer visual.

**Architecture:** Augments are non-mutating — stored in `player.augments` list, applied at use-time via `effective_*()` methods on top of already-upgraded stats. Room reward screen replaces the old "ROOM CLEAR + SPACE" flow. Pause screen accessible via ESC during ENCOUNTER or REWARD.

**Tech Stack:** Python 3.12, Pygame 2.x, unittest

---

## File Map

| File | Changes |
|---|---|
| `settings.py` | Add `AUGMENTS` dict with 5 augments + colors; add `augments` pool list to each weapon def |
| `entities/player.py` | `equip_augment()`, `effective_*()` methods, `try_fire()` + reload use effective methods, `draw_laser()`, random start weapon |
| `entities/projectile.py` | `Bullet`: `pierce_count`/`pierce_damage_mult` params + `on_hit()` method |
| `systems/run_manager.py` | `update()` skips REWARD on last room → WIN directly |
| `ui/hud.py` | `draw_reward()`, `draw_pause()`, augment slot squares + `effective_mag_size()` in `draw()` |
| `main.py` | Manual bullet collision loop; REWARD card generation + input; `paused` flag; ESC = pause; Q = quit; remove ESC-quits |
| `tests/test_player_augments.py` | New — augment methods, effective stats, try_fire pierce, random weapon, draw_laser |
| `tests/test_bullet_pierce.py` | New — `on_hit()` pierce behavior |
| `tests/test_run_manager.py` | Update `test_transitions_to_reward_when_room_complete` + add last-room WIN test |
| `tests/test_hud_m10.py` | New — draw_reward, draw_pause, augment squares smoke tests |

---

## Task 1: AUGMENTS data + weapon pools

**Files:**
- Modify: `settings.py`
- Test: `tests/test_augments_settings.py` (new)

- [ ] **Step 1: Write failing tests**

```python
# tests/test_augments_settings.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest


class TestAugmentsSettings(unittest.TestCase):
    def test_augments_dict_exists(self):
        from settings import AUGMENTS
        self.assertIsInstance(AUGMENTS, dict)

    def test_five_augments_defined(self):
        from settings import AUGMENTS
        self.assertEqual(len(AUGMENTS), 5)

    def test_hollow_point_has_pierce_behavior(self):
        from settings import AUGMENTS
        hp = AUGMENTS['hollow_point']
        self.assertEqual(hp['pierce_count'], 1)
        self.assertAlmostEqual(hp['pierce_damage_mult'], 0.5)

    def test_drum_mag_has_mag_size_mult(self):
        from settings import AUGMENTS
        self.assertAlmostEqual(AUGMENTS['drum_mag']['mag_size_mult'], 2.0)

    def test_fast_loader_has_reload_time_mult(self):
        from settings import AUGMENTS
        self.assertAlmostEqual(AUGMENTS['fast_loader']['reload_time_mult'], 0.75)

    def test_more_pellets_has_pellet_bonus(self):
        from settings import AUGMENTS
        self.assertEqual(AUGMENTS['more_pellets']['pellet_bonus'], 2)

    def test_laser_pointer_has_no_stat_keys(self):
        from settings import AUGMENTS
        lp = AUGMENTS['laser_pointer']
        for key in ('damage_mult', 'reload_time_mult', 'mag_size_mult', 'pierce_count', 'pellet_bonus'):
            self.assertNotIn(key, lp)

    def test_all_augments_have_color(self):
        from settings import AUGMENTS
        for aid, aug in AUGMENTS.items():
            self.assertIn('color', aug, f"{aid} missing color")

    def test_all_augments_have_id_name_desc(self):
        from settings import AUGMENTS
        for aug in AUGMENTS.values():
            self.assertIn('id', aug)
            self.assertIn('name', aug)
            self.assertIn('desc', aug)

    def test_pistol_has_augments_pool(self):
        from settings import WEAPONS
        self.assertIn('augments', WEAPONS['pistol'])

    def test_shotgun_has_augments_pool(self):
        from settings import WEAPONS
        self.assertIn('augments', WEAPONS['shotgun'])

    def test_pistol_pool_has_hollow_point(self):
        from settings import WEAPONS
        self.assertIn('hollow_point', WEAPONS['pistol']['augments'])

    def test_pistol_pool_excludes_more_pellets(self):
        from settings import WEAPONS
        self.assertNotIn('more_pellets', WEAPONS['pistol']['augments'])

    def test_shotgun_pool_has_more_pellets(self):
        from settings import WEAPONS
        self.assertIn('more_pellets', WEAPONS['shotgun']['augments'])

    def test_shotgun_pool_excludes_hollow_point(self):
        from settings import WEAPONS
        self.assertNotIn('hollow_point', WEAPONS['shotgun']['augments'])

    def test_both_pools_share_laser_fast_drum(self):
        from settings import WEAPONS
        shared = {'laser_pointer', 'fast_loader', 'drum_mag'}
        self.assertTrue(shared.issubset(set(WEAPONS['pistol']['augments'])))
        self.assertTrue(shared.issubset(set(WEAPONS['shotgun']['augments'])))

    def test_all_pool_ids_exist_in_augments(self):
        from settings import WEAPONS, AUGMENTS
        for weapon in WEAPONS.values():
            for aid in weapon['augments']:
                self.assertIn(aid, AUGMENTS, f"pool references unknown augment: {aid}")


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python -m pytest tests/test_augments_settings.py -v
```

Expected: multiple failures — `AUGMENTS` doesn't exist yet, weapon defs have no `augments` key.

- [ ] **Step 3: Implement AUGMENTS dict and weapon pools in `settings.py`**

Add after the `WEAPONS` dict:

```python
# Augments — weapon-specific power-ups awarded at room-clear reward screens
AUGMENTS = {
    'laser_pointer': {
        'id': 'laser_pointer',
        'name': 'Laser Sight',
        'desc': 'Shows aiming line to target',
        'color': (200, 80, 80),
    },
    'fast_loader': {
        'id': 'fast_loader',
        'name': 'Fast Loader',
        'desc': '-25% reload time',
        'reload_time_mult': 0.75,
        'color': (80, 200, 200),
    },
    'hollow_point': {
        'id': 'hollow_point',
        'name': 'Hollow Point',
        'desc': 'Bullets pierce one enemy (50% dmg)',
        'pierce_count': 1,
        'pierce_damage_mult': 0.5,
        'color': (220, 180, 40),
    },
    'drum_mag': {
        'id': 'drum_mag',
        'name': 'Drum Mag',
        'desc': 'Double mag size on reload',
        'mag_size_mult': 2.0,
        'color': (120, 200, 80),
    },
    'more_pellets': {
        'id': 'more_pellets',
        'name': 'More Pellets',
        'desc': '+2 pellets, same spread',
        'pellet_bonus': 2,
        'color': (200, 120, 40),
    },
}
```

Add `augments` list to each weapon def inside `WEAPONS`:

```python
WEAPONS = {
    'pistol': {
        'name': 'Pistol',
        'damage': 55,
        'mag_size': 6,
        'reload_time': 1.2,
        'shot_cooldown': 0.4,
        'pellets': 1,
        'spread': 0.0,
        'augments': ['laser_pointer', 'fast_loader', 'hollow_point', 'drum_mag'],
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
        'augments': ['laser_pointer', 'fast_loader', 'more_pellets', 'drum_mag'],
        'bullet': {
            'speed': 500,
            'radius': 4,
            'color': (255, 165, 0),
            'shape': 'circle',
        },
    },
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_augments_settings.py -v
```

Expected: all 17 tests pass.

- [ ] **Step 5: Commit**

```bash
git add settings.py tests/test_augments_settings.py
git commit -m "feat: add AUGMENTS dict and weapon augment pools to settings"
```

---

## Task 2: Player augment methods

**Files:**
- Modify: `entities/player.py`
- Test: `tests/test_player_augments.py` (new)

- [ ] **Step 1: Write failing tests**

```python
# tests/test_player_augments.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest
from unittest.mock import patch


def _player():
    from entities.player import Player
    return Player()


class TestEquipAugment(unittest.TestCase):
    def test_equip_augment_appends_to_list(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        self.assertEqual(len(p.augments), 1)
        self.assertEqual(p.augments[0]['id'], 'drum_mag')

    def test_equip_augment_max_two(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip_augment(AUGMENTS['fast_loader'])
        p.equip_augment(AUGMENTS['laser_pointer'])  # silently ignored
        self.assertEqual(len(p.augments), 2)

    def test_augments_clear_on_weapon_swap(self):
        from settings import AUGMENTS, WEAPONS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.augments, [])


class TestEffectiveMethods(unittest.TestCase):
    def test_effective_damage_no_augments(self):
        p = _player()
        self.assertEqual(p.effective_damage(), p.damage)

    def test_effective_damage_with_damage_mult(self):
        p = _player()
        base = p.damage
        p.augments = [{'damage_mult': 1.5}]
        self.assertEqual(p.effective_damage(), int(base * 1.5))

    def test_effective_reload_time_no_augments(self):
        p = _player()
        self.assertAlmostEqual(p.effective_reload_time(), p.reload_time)

    def test_effective_reload_time_with_fast_loader(self):
        from settings import AUGMENTS
        p = _player()
        base = p.reload_time
        p.equip_augment(AUGMENTS['fast_loader'])
        self.assertAlmostEqual(p.effective_reload_time(), base * 0.75)

    def test_effective_mag_size_no_augments(self):
        p = _player()
        self.assertEqual(p.effective_mag_size(), p.mag_size)

    def test_effective_mag_size_with_drum_mag(self):
        from settings import AUGMENTS
        p = _player()
        base = p.mag_size
        p.equip_augment(AUGMENTS['drum_mag'])
        self.assertEqual(p.effective_mag_size(), int(base * 2.0))

    def test_effective_pellets_no_augments(self):
        p = _player()
        self.assertEqual(p.effective_pellets(), p.weapon['pellets'])

    def test_effective_pellets_with_more_pellets(self):
        from settings import AUGMENTS, WEAPONS
        p = _player()
        p.equip(WEAPONS['shotgun'])
        p.equip_augment(AUGMENTS['more_pellets'])
        self.assertEqual(p.effective_pellets(), 6)

    def test_effective_pierce_no_augments(self):
        p = _player()
        count, mult = p.effective_pierce()
        self.assertEqual(count, 0)

    def test_effective_pierce_with_hollow_point(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['hollow_point'])
        count, mult = p.effective_pierce()
        self.assertEqual(count, 1)
        self.assertAlmostEqual(mult, 0.5)

    def test_effective_methods_stack_multiplicatively(self):
        p = _player()
        base = p.reload_time
        p.augments = [{'reload_time_mult': 0.75}, {'reload_time_mult': 0.75}]
        self.assertAlmostEqual(p.effective_reload_time(), base * 0.75 * 0.75)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_player_augments.py -v
```

Expected: failures on `equip_augment`, `effective_damage`, `effective_reload_time`, etc.

- [ ] **Step 3: Implement `equip_augment()` and `effective_*()` in `entities/player.py`**

Add after the `equip()` method:

```python
def equip_augment(self, augment_def):
    if len(self.augments) < 2:
        self.augments.append(augment_def)

def effective_damage(self):
    m = 1.0
    for a in self.augments:
        m *= a.get('damage_mult', 1.0)
    return int(self.damage * m)

def effective_reload_time(self):
    m = 1.0
    for a in self.augments:
        m *= a.get('reload_time_mult', 1.0)
    return self.reload_time * m

def effective_mag_size(self):
    m = 1.0
    for a in self.augments:
        m *= a.get('mag_size_mult', 1.0)
    return int(self.mag_size * m)

def effective_pellets(self):
    bonus = sum(a.get('pellet_bonus', 0) for a in self.augments)
    return self.weapon['pellets'] + bonus

def effective_pierce(self):
    for a in self.augments:
        if 'pierce_count' in a:
            return a['pierce_count'], a.get('pierce_damage_mult', 0.5)
    return 0, 0.5
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_player_augments.py -v
```

Expected: all 14 tests pass.

- [ ] **Step 5: Commit**

```bash
git add entities/player.py tests/test_player_augments.py
git commit -m "feat: add equip_augment() and effective_*() methods to Player"
```

---

## Task 3: Bullet pierce — `on_hit()` method

**Files:**
- Modify: `entities/projectile.py`
- Test: `tests/test_bullet_pierce.py` (new)

- [ ] **Step 1: Write failing tests**

```python
# tests/test_bullet_pierce.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest


def _bullet(pierce_count=0, pierce_damage_mult=0.5, damage=100):
    from entities.projectile import Bullet
    return Bullet(
        (100, 100), pygame.math.Vector2(1, 0), damage,
        4, (255, 255, 0), 'circle', 500,
        pierce_count=pierce_count, pierce_damage_mult=pierce_damage_mult,
    )


class MockEnemy:
    def __init__(self):
        self.damage_received = []
    def take_damage(self, amount):
        self.damage_received.append(amount)
        return False


class TestBulletPierce(unittest.TestCase):
    def test_default_pierce_count_is_zero(self):
        from entities.projectile import Bullet
        b = Bullet((0, 0), pygame.math.Vector2(1, 0), 55, 4, (255, 255, 0), 'circle', 500)
        self.assertEqual(b.pierce_count, 0)

    def test_pierce_count_stored(self):
        b = _bullet(pierce_count=1)
        self.assertEqual(b.pierce_count, 1)

    def test_on_hit_no_pierce_returns_true(self):
        b = _bullet(pierce_count=0)
        result = b.on_hit(MockEnemy())
        self.assertTrue(result)

    def test_on_hit_no_pierce_deals_full_damage(self):
        b = _bullet(pierce_count=0, damage=55)
        e = MockEnemy()
        b.on_hit(e)
        self.assertEqual(e.damage_received, [55])

    def test_on_hit_pierce_returns_false(self):
        b = _bullet(pierce_count=1)
        result = b.on_hit(MockEnemy())
        self.assertFalse(result)

    def test_on_hit_pierce_deals_full_damage_to_first_enemy(self):
        b = _bullet(pierce_count=1, damage=100)
        e = MockEnemy()
        b.on_hit(e)
        self.assertEqual(e.damage_received, [100])

    def test_on_hit_pierce_halves_damage(self):
        b = _bullet(pierce_count=1, pierce_damage_mult=0.5, damage=100)
        b.on_hit(MockEnemy())
        self.assertEqual(b.damage, 50)

    def test_on_hit_pierce_decrements_count(self):
        b = _bullet(pierce_count=1)
        b.on_hit(MockEnemy())
        self.assertEqual(b.pierce_count, 0)

    def test_on_hit_second_hit_returns_true(self):
        b = _bullet(pierce_count=1)
        b.on_hit(MockEnemy())   # pierces first
        result = b.on_hit(MockEnemy())
        self.assertTrue(result)

    def test_on_hit_second_hit_deals_halved_damage(self):
        b = _bullet(pierce_count=1, pierce_damage_mult=0.5, damage=100)
        b.on_hit(MockEnemy())   # pierces: damage → 50
        e2 = MockEnemy()
        b.on_hit(e2)
        self.assertEqual(e2.damage_received, [50])


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_bullet_pierce.py -v
```

Expected: failures — `Bullet` doesn't accept `pierce_count` kwarg yet, `on_hit` doesn't exist.

- [ ] **Step 3: Implement pierce params and `on_hit()` in `entities/projectile.py`**

Update `Bullet.__init__` signature and add `on_hit()`:

```python
class Bullet(Projectile):
    def __init__(self, pos, direction, damage, radius, color, shape, speed,
                 pierce_count=0, pierce_damage_mult=0.5):
        super().__init__(pos, direction, speed, radius, damage)
        self.color = color
        self.shape = shape
        self.pierce_count = pierce_count
        self.pierce_damage_mult = pierce_damage_mult

    def on_hit(self, enemy):
        """Deal damage to enemy. Returns True if bullet should die, False if it pierces."""
        enemy.take_damage(self.damage)
        if self.pierce_count > 0:
            self.damage = int(self.damage * self.pierce_damage_mult)
            self.pierce_count -= 1
            return False
        return True

    def draw(self, surface):
        # ... (unchanged)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_bullet_pierce.py -v
```

Expected: all 10 tests pass. Also run existing bullet tests to confirm no regression:

```bash
python -m pytest tests/test_bullet.py -v
```

Expected: all 8 existing tests still pass.

- [ ] **Step 5: Commit**

```bash
git add entities/projectile.py tests/test_bullet_pierce.py
git commit -m "feat: add pierce mechanics to Bullet — pierce_count, pierce_damage_mult, on_hit()"
```

---

## Task 4: `try_fire()` and reload use effective methods

**Files:**
- Modify: `entities/player.py`
- Test: `tests/test_player_augments.py` (extend)

- [ ] **Step 1: Add failing tests to `tests/test_player_augments.py`**

Append this class to the file:

```python
class TestTryFireEffectiveMethods(unittest.TestCase):
    def test_try_fire_uses_effective_damage(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['hollow_point'])  # hollow_point has no damage_mult
        # Use a raw augment with damage_mult to test
        p.augments = [{'damage_mult': 2.0}]
        base_damage = p.damage
        bullets = p.try_fire()
        self.assertEqual(bullets[0].damage, int(base_damage * 2.0))

    def test_try_fire_uses_effective_pellets_for_shotgun(self):
        from settings import AUGMENTS, WEAPONS
        p = _player()
        p.equip(WEAPONS['shotgun'])
        p.equip_augment(AUGMENTS['more_pellets'])
        bullets = p.try_fire()
        self.assertEqual(len(bullets), 6)

    def test_try_fire_passes_pierce_count_to_bullets(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['hollow_point'])
        bullets = p.try_fire()
        self.assertEqual(bullets[0].pierce_count, 1)

    def test_reload_fills_to_effective_mag_size(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        expected = p.effective_mag_size()
        p.ammo = 0
        p.try_reload()
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(p.effective_reload_time() + 0.1)
        self.assertEqual(p.ammo, expected)

    def test_reload_uses_effective_reload_time(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['fast_loader'])
        p.ammo = 0
        p.try_reload()
        # Should NOT complete before effective_reload_time
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(p.effective_reload_time() - 0.1)
        self.assertFalse(p.reload_complete)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_player_augments.py::TestTryFireEffectiveMethods -v
```

Expected: failures — `try_fire()` still uses `self.damage` and `weapon['pellets']` directly.

- [ ] **Step 3: Update `try_fire()` and reload in `entities/player.py`**

Replace `try_fire()` body:

```python
def try_fire(self):
    """Return list of Bullets; empty list means cannot fire."""
    if self.reloading or self._shot_cooldown > 0 or self.ammo <= 0:
        return []
    self.ammo -= 1
    self._shot_cooldown = self.shot_cooldown_base

    weapon = self.weapon
    pellets = self.effective_pellets()
    spread = weapon['spread']
    bdef = weapon['bullet']
    pierce_count, pierce_damage_mult = self.effective_pierce()

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
        Bullet(
            self.pos, d, self.effective_damage(),
            bdef['radius'], bdef['color'], bdef['shape'], bdef['speed'],
            pierce_count=pierce_count, pierce_damage_mult=pierce_damage_mult,
        )
        for d in directions
    ]
```

Update the reload completion line in `update()` (find `self.ammo = self.mag_size`):

```python
if self.reload_progress >= 1.0:
    self.ammo = self.effective_mag_size()
    self.reloading = False
    self.reload_complete = True
```

Also update reload progress tick (find `self.reload_progress + dt / self.reload_time`):

```python
self.reload_progress = min(1.0, self.reload_progress + dt / self.effective_reload_time())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_player_augments.py -v
python -m pytest tests/test_player_equip.py -v
```

Expected: all tests in both files pass.

- [ ] **Step 5: Commit**

```bash
git add entities/player.py tests/test_player_augments.py
git commit -m "feat: try_fire() and reload use effective_*() methods"
```

---

## Task 5: Random starting weapon

**Files:**
- Modify: `entities/player.py`
- Modify: `tests/test_player_equip.py` (update one test)

- [ ] **Step 1: Update the broken test in `tests/test_player_equip.py`**

Find and replace `test_player_starts_with_pistol`:

```python
def test_player_starts_with_valid_weapon(self):
    from settings import WEAPONS
    p = _player()
    self.assertIn(p.weapon, WEAPONS.values())
```

- [ ] **Step 2: Add probabilistic start test to `tests/test_player_augments.py`**

Append to `tests/test_player_augments.py`:

```python
class TestRandomStartingWeapon(unittest.TestCase):
    def test_starting_weapon_is_valid(self):
        from settings import WEAPONS
        p = _player()
        self.assertIn(p.weapon, WEAPONS.values())

    def test_multiple_starts_can_differ(self):
        from settings import WEAPONS
        names = {_player().weapon['name'] for _ in range(30)}
        self.assertGreater(len(names), 1, "Starting weapon never varied across 30 instances")
```

- [ ] **Step 3: Run tests to show current state**

```bash
python -m pytest tests/test_player_equip.py::TestPlayerEquip::test_player_starts_with_valid_weapon tests/test_player_augments.py::TestRandomStartingWeapon -v
```

Expected: `test_starting_weapon_is_valid` passes (pistol is a valid weapon), `test_multiple_starts_can_differ` fails (always pistol).

- [ ] **Step 4: Implement random starting weapon in `entities/player.py`**

Add `import random` at the top of the file (after existing imports).

Replace `self.equip(WEAPONS['pistol'])` in `__init__` with:

```python
self.equip(random.choice(list(WEAPONS.values())))
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_player_equip.py tests/test_player_augments.py -v
```

Expected: all tests pass including `test_multiple_starts_can_differ`.

- [ ] **Step 6: Commit**

```bash
git add entities/player.py tests/test_player_equip.py tests/test_player_augments.py
git commit -m "feat: player starts with a random weapon each run"
```

---

## Task 6: RunManager — skip REWARD on last room

**Files:**
- Modify: `systems/run_manager.py`
- Modify: `tests/test_run_manager.py` (update one test + add one)

- [ ] **Step 1: Update and add tests in `tests/test_run_manager.py`**

Find `test_transitions_to_reward_when_room_complete` and update it to use a 2-room sequence (non-last room):

```python
def test_transitions_to_reward_on_non_last_room(self):
    seq = [
        {'type': 'survive', 'duration': 1, 'difficulty': 1.0},
        {'type': 'survive', 'duration': 90, 'difficulty': 1.0},
    ]
    rm = self._make(seq)
    rm.update(1.1)
    self.assertEqual(rm.state, 'REWARD')
```

Add a new test in `TestRunManager`:

```python
def test_last_room_complete_goes_to_win_not_reward(self):
    rm = self._make([{'type': 'survive', 'duration': 1, 'difficulty': 1.0}])
    rm.update(1.1)
    self.assertEqual(rm.state, 'WIN')
```

- [ ] **Step 2: Run tests to show current state**

```bash
python -m pytest tests/test_run_manager.py::TestRunManager::test_last_room_complete_goes_to_win_not_reward -v
```

Expected: FAIL — currently goes to REWARD.

- [ ] **Step 3: Update `update()` in `systems/run_manager.py`**

Find the `if self._current_room.is_complete:` block in `update()` and replace it:

```python
if self._current_room.is_complete:
    if self._room_idx >= len(self._sequence) - 1:
        self._state = 'WIN'
    else:
        self._state = 'REWARD'
```

- [ ] **Step 4: Run all run_manager tests**

```bash
python -m pytest tests/test_run_manager.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add systems/run_manager.py tests/test_run_manager.py
git commit -m "feat: last room completion transitions to WIN directly, skipping reward screen"
```

---

## Task 7: Manual bullet collision loop in `main.py`

**Files:**
- Modify: `main.py`

No unit tests for this (main.py uses asyncio.run at module level; tested via manual play-test in Task 12).

- [ ] **Step 1: Replace `groupcollide` with manual pierce-aware loop**

In `main.py`, find the collision block (around line 112):

```python
hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
for bullet, hit_enemies in hits.items():
    for enemy in hit_enemies:
        if enemy.take_damage(bullet.damage):
            orb = XPOrb(enemy.pos, enemy.xp_value)
            all_sprites.add(orb)
            xp_orbs.add(orb)
            run_manager.record_kill()
```

Replace with:

```python
for bullet in list(bullets):  # copy — safe to kill during iteration
    for enemy in pygame.sprite.spritecollide(bullet, enemies, False):
        bullet_died = bullet.on_hit(enemy)
        if not enemy.alive():
            orb = XPOrb(enemy.pos, enemy.xp_value)
            all_sprites.add(orb)
            xp_orbs.add(orb)
            run_manager.record_kill()
        if bullet_died:
            bullet.kill()
            break
```

- [ ] **Step 2: Run existing tests to confirm no regressions**

```bash
python -m pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: replace groupcollide with pierce-aware bullet collision loop"
```

---

## Task 8: Laser pointer — `draw_laser()` on Player

**Files:**
- Modify: `entities/player.py`
- Test: `tests/test_player_augments.py` (extend)

- [ ] **Step 1: Add smoke test**

Append to `tests/test_player_augments.py`:

```python
class TestDrawLaser(unittest.TestCase):
    def test_draw_laser_does_not_raise_without_augment(self):
        import pygame
        p = _player()
        surf = pygame.Surface((1280, 720))
        enemies = pygame.sprite.Group()
        p.draw_laser(surf, enemies)  # should not raise

    def test_draw_laser_does_not_raise_with_laser_augment(self):
        import pygame
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['laser_pointer'])
        surf = pygame.Surface((1280, 720))
        enemies = pygame.sprite.Group()
        p.draw_laser(surf, enemies)  # should not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_player_augments.py::TestDrawLaser -v
```

Expected: `AttributeError: 'Player' object has no attribute 'draw_laser'`

- [ ] **Step 3: Add `draw_laser()` to `entities/player.py`**

Add after the `draw()` method:

```python
def draw_laser(self, surface, enemies):
    """Draw laser pointer line if laser_pointer augment is active."""
    if not any(a.get('id') == 'laser_pointer' for a in self.augments):
        return

    MAX_RANGE = 300
    start = pygame.math.Vector2(self.rect.center)
    end = start + self.facing * MAX_RANGE

    # Find nearest enemy hit by ray
    nearest_end = end
    nearest_dist_sq = MAX_RANGE * MAX_RANGE + 1
    for enemy in enemies:
        hit = enemy.rect.clipline(
            (int(start.x), int(start.y)),
            (int(end.x), int(end.y)),
        )
        if hit:
            hit_pt = pygame.math.Vector2(hit[0])
            dist_sq = (hit_pt - start).length_squared()
            if dist_sq < nearest_dist_sq:
                nearest_dist_sq = dist_sq
                nearest_end = hit_pt

    # Draw on a temporary SRCALPHA surface so we can set alpha
    laser_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    sx, sy = int(start.x), int(start.y)
    ex, ey = int(nearest_end.x), int(nearest_end.y)
    pygame.draw.line(laser_surf, (180, 0, 0, 80), (sx, sy), (ex, ey), 3)   # dim glow
    pygame.draw.line(laser_surf, (255, 60, 60, 220), (sx, sy), (ex, ey), 1) # bright core
    surface.blit(laser_surf, (0, 0))
```

- [ ] **Step 4: Wire `draw_laser()` into the main draw loop**

In `main.py`, after the entity draw loop (`for entity in all_sprites: entity.draw(screen)`), add:

```python
player.draw_laser(screen, enemies)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest tests/test_player_augments.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add entities/player.py main.py tests/test_player_augments.py
git commit -m "feat: laser pointer augment — draw_laser() raycasts to nearest enemy"
```

---

## Task 9: HUD augment squares + ammo denominator

**Files:**
- Modify: `ui/hud.py`
- Test: `tests/test_hud_m10.py` (new)

- [ ] **Step 1: Write smoke test**

```python
# tests/test_hud_m10.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest


def _hud():
    from ui.hud import HUD
    return HUD()


def _player():
    from entities.player import Player
    return Player()


class TestHudAugmentSquares(unittest.TestCase):
    def test_draw_with_no_augments_does_not_raise(self):
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        hud.draw(surf, p)

    def test_draw_with_two_augments_does_not_raise(self):
        from settings import AUGMENTS
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip_augment(AUGMENTS['fast_loader'])
        hud.draw(surf, p)

    def test_ammo_display_uses_effective_mag_size(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.ammo = 12  # simulating post-reload with drum mag
        # effective_mag_size returns 12, so display should be "12 / 12"
        # We just confirm no crash and that the method exists
        self.assertEqual(p.effective_mag_size(), p.mag_size * 2)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they pass (smoke only — base draw already works)**

```bash
python -m pytest tests/test_hud_m10.py::TestHudAugmentSquares -v
```

Expected: all 3 pass (base draw works; we haven't changed HUD yet).

- [ ] **Step 3: Update `draw()` in `ui/hud.py` — augment squares + effective_mag_size**

In the `draw()` method, find the ammo label rendering (around `ammo_key = (player.ammo, player.mag_size)`):

```python
ammo_key = (player.ammo, player.effective_mag_size())
if ammo_key != self._cached_ammo_key:
    self._label, _ = self._font.render(
        f"{player.ammo} / {player.effective_mag_size()}", HUD_COLOR_AMMO)
    self._cached_ammo_key = ammo_key
```

Find the weapon name rendering block and append augment squares immediately after the `surface.blit(self._weapon_label, ...)` line:

```python
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
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_hud_m10.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add ui/hud.py tests/test_hud_m10.py
git commit -m "feat: HUD shows augment slot squares next to weapon name, ammo uses effective_mag_size"
```

---

## Task 10: `draw_reward()` in HUD

**Files:**
- Modify: `ui/hud.py`
- Test: `tests/test_hud_m10.py` (extend)

- [ ] **Step 1: Add failing test to `tests/test_hud_m10.py`**

Append:

```python
class TestDrawReward(unittest.TestCase):
    def _cards(self):
        from settings import AUGMENTS, WEAPONS
        return [
            {'type': 'weapon', 'weapon_def': WEAPONS['shotgun']},
            {'type': 'augment', 'augment_def': AUGMENTS['drum_mag']},
            {'type': 'augment', 'augment_def': AUGMENTS['fast_loader']},
        ]

    def test_draw_reward_does_not_raise(self):
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        hud.draw_reward(surf, p, self._cards(), (0, 0))

    def test_draw_reward_with_full_augments_does_not_raise(self):
        from settings import AUGMENTS
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip_augment(AUGMENTS['fast_loader'])
        hud.draw_reward(surf, p, self._cards(), (0, 0))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_hud_m10.py::TestDrawReward -v
```

Expected: `AttributeError: 'HUD' object has no attribute 'draw_reward'`

- [ ] **Step 3: Add `draw_reward()` to `ui/hud.py`**

Add after `draw_room_clear()`:

```python
def draw_reward(self, surface, player, cards, mouse_pos):
    hover_idx = self.hovered_upgrade(mouse_pos)
    augments_full = len(player.augments) >= 2

    self._overlay_surf.fill((0, 0, 0, 180))

    # Title
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

        # Key number
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

        else:  # augment card
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
```

Also add `WIDTH` and `HEIGHT` to the imports at the top of `hud.py` if not already imported (they are: `from settings import WIDTH, HEIGHT, ...`).

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_hud_m10.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add ui/hud.py tests/test_hud_m10.py
git commit -m "feat: HUD draw_reward() — 3-card room reward screen"
```

---

## Task 11: `draw_pause()` in HUD

**Files:**
- Modify: `ui/hud.py`
- Modify: `settings.py` (import UPGRADES needed in hud)
- Test: `tests/test_hud_m10.py` (extend)

- [ ] **Step 1: Add failing test**

Append to `tests/test_hud_m10.py`:

```python
class TestDrawPause(unittest.TestCase):
    def test_draw_pause_no_upgrades_does_not_raise(self):
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        hud.draw_pause(surf, p)

    def test_draw_pause_with_upgrades_and_augments_does_not_raise(self):
        from settings import AUGMENTS
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        p.apply_upgrade('damage')
        p.apply_upgrade('reload')
        p.apply_upgrade('damage')
        p.equip_augment(AUGMENTS['drum_mag'])
        hud.draw_pause(surf, p)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_hud_m10.py::TestDrawPause -v
```

Expected: `AttributeError: 'HUD' object has no attribute 'draw_pause'`

- [ ] **Step 3: Add `UPGRADES` to `hud.py` imports**

In `ui/hud.py`, add `UPGRADES` to the settings import:

```python
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
```

- [ ] **Step 4: Add `draw_pause()` to `ui/hud.py`**

Add after `draw_reward()`:

```python
def draw_pause(self, surface, player):
    from collections import Counter
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))

    # Title
    title_surf, title_rect = self._font_large.render('PAUSED', (220, 220, 220))
    overlay.blit(title_surf, ((WIDTH - title_rect.width) // 2, 60))

    col_y = 160
    col_left = WIDTH // 2 - 260
    col_right = WIDTH // 2 + 40

    # Left column — upgrades
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

    # Right column — weapon + augments
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

    # Footer
    footer_surf, footer_rect = self._font_small.render(
        'ESC  resume        Q  quit', (140, 140, 140))
    overlay.blit(footer_surf, ((WIDTH - footer_rect.width) // 2, HEIGHT - 50))

    surface.blit(overlay, (0, 0))
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_hud_m10.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add ui/hud.py tests/test_hud_m10.py
git commit -m "feat: HUD draw_pause() — upgrade history + weapon/augments overlay"
```

---

## Task 12: Wire everything into `main.py`

**Files:**
- Modify: `main.py`

This task wires reward card generation, REWARD state input handling, pause toggle (ESC), and Q-to-quit. Tested manually in play-test.

- [ ] **Step 1: Update imports at the top of `main.py`**

Add `AUGMENTS` to the settings import:

```python
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES,
    HIT_FLASH_COLOR, HIT_FLASH_DURATION, HIT_FLASH_ALPHA_MAX,
    SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE,
    ROOM_SEQUENCE, WEAPONS, AUGMENTS, ROOM_HEAL_FRACTION,
)
```

- [ ] **Step 2: Add helper functions before `new_game()`**

```python
def _generate_reward_cards(player):
    """1 weapon card + 2 augment cards from current weapon's pool."""
    other_weapon = next(w for w in WEAPONS.values() if w is not player.weapon)
    weapon_card = {'type': 'weapon', 'weapon_def': other_weapon}
    pool_ids = player.weapon['augments']
    equipped_ids = {a['id'] for a in player.augments}
    available = [AUGMENTS[aid] for aid in pool_ids if aid not in equipped_ids]
    aug_cards = [
        {'type': 'augment', 'augment_def': a}
        for a in random.sample(available, min(2, len(available)))
    ]
    return [weapon_card] + aug_cards


def _apply_reward_card(card, player):
    if card['type'] == 'weapon':
        player.equip(card['weapon_def'])
    elif card['type'] == 'augment':
        player.equip_augment(card['augment_def'])
```

- [ ] **Step 3: Add `paused` and `reward_cards` state variables**

In `async def main()`, after `level_up = False` and `pending_upgrades = []` add:

```python
paused = False
reward_cards = []
```

Also add them to the reset inside the `new_game()` re-call block (find where `level_up = False` is reset after R key on WIN/GAME_OVER):

```python
level_up = False
pending_upgrades = []
paused = False
reward_cards = []
```

- [ ] **Step 4: Replace ESC-quits with pause toggle, update REWARD handler, add Q-quit**

Replace the entire event loop section. Find the event loop starting at `for event in pygame.event.get():` and replace its content:

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False

    elif paused:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = False
            elif event.key == pygame.K_q:
                running = False

    elif run_manager.state in ('WIN', 'GAME_OVER'):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            player, all_sprites, enemies, bullets, enemy_projectiles, xp_orbs, spawner, run_manager = new_game()
            level_up = False
            pending_upgrades = []
            paused = False
            reward_cards = []

    elif run_manager.state == 'REWARD':
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            paused = not paused
        elif event.type == pygame.KEYDOWN:
            idx = event.key - pygame.K_1
            if 0 <= idx < len(reward_cards):
                card = reward_cards[idx]
                if not (card['type'] == 'augment' and len(player.augments) >= 2):
                    _apply_reward_card(card, player)
                    reward_cards = []
                    for e in list(enemies): e.kill()
                    for p in list(enemy_projectiles): p.kill()
                    for o in list(xp_orbs): o.kill()
                    run_manager.advance()
                    if run_manager.state == 'ENCOUNTER':
                        player.heal(ROOM_HEAL_FRACTION)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = hud.hovered_upgrade(event.pos)
            if idx >= 0 and idx < len(reward_cards):
                card = reward_cards[idx]
                if not (card['type'] == 'augment' and len(player.augments) >= 2):
                    _apply_reward_card(card, player)
                    reward_cards = []
                    for e in list(enemies): e.kill()
                    for p in list(enemy_projectiles): p.kill()
                    for o in list(xp_orbs): o.kill()
                    run_manager.advance()
                    if run_manager.state == 'ENCOUNTER':
                        player.heal(ROOM_HEAL_FRACTION)

    elif level_up:
        if event.type == pygame.KEYDOWN:
            idx = event.key - pygame.K_1
            if 0 <= idx < len(pending_upgrades):
                player.apply_upgrade(pending_upgrades[idx]['id'])
                level_up = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = hud.hovered_upgrade(event.pos)
            if idx >= 0:
                player.apply_upgrade(pending_upgrades[idx]['id'])
                level_up = False

    else:  # ENCOUNTER, not paused, not level_up
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused
            elif event.key == pygame.K_r:
                player.try_reload()
            # DEV ONLY — Tab toggles weapon for testing
            elif event.key == pygame.K_TAB:
                if player.weapon is WEAPONS['pistol']:
                    player.equip(WEAPONS['shotgun'])
                else:
                    player.equip(WEAPONS['pistol'])
                print(f"[DEV] weapon: {player.weapon['name']}")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            fired = player.try_fire()
            if fired:
                for bullet in fired:
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                sounds.play_gunshot()
```

- [ ] **Step 5: Generate reward cards on REWARD transition**

Inside the `if run_manager.state == 'ENCOUNTER' and not level_up and not paused:` block, add the card generation check immediately after `all_sprites.update(dt, player)`. All existing spawner + collision code stays in place beneath it:

```python
if run_manager.state == 'ENCOUNTER' and not level_up and not paused:
    run_manager.update(dt)
    all_sprites.update(dt, player)

    # Generate reward cards the frame the room completes
    if run_manager.state == 'REWARD' and not reward_cards:
        reward_cards = _generate_reward_cards(player)

    if run_manager.current_room.spawns_waves:
        wp = run_manager.wave_manager.params
        spawner.update(dt, all_sprites, enemies, enemy_projectiles,
                       spawn_interval=wp['spawn_interval'],
                       mutant_ratio=wp['mutant_ratio'],
                       hp_mult=wp['hp_mult'])

    for bullet in list(bullets):
        for enemy in pygame.sprite.spritecollide(bullet, enemies, False):
            bullet_died = bullet.on_hit(enemy)
            if not enemy.alive():
                orb = XPOrb(enemy.pos, enemy.xp_value)
                all_sprites.add(orb)
                xp_orbs.add(orb)
                run_manager.record_kill()
            if bullet_died:
                bullet.kill()
                break

    for proj in pygame.sprite.spritecollide(player, enemy_projectiles, True):
        player.take_damage(proj.damage)

    # ... sound signals and player.dead checks unchanged below ...
```

- [ ] **Step 6: Update the draw section**

Replace the REWARD draw call:

```python
# OLD:
if run_manager.state == 'REWARD':
    hud.draw_room_clear(screen)

# NEW:
if run_manager.state == 'REWARD':
    hud.draw_reward(screen, player, reward_cards, pygame.mouse.get_pos())
```

Add pause overlay draw (after the level_up and REWARD draws):

```python
if paused:
    hud.draw_pause(screen, player)
```

- [ ] **Step 7: Run all tests**

```bash
python -m pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 8: Commit**

```bash
git add main.py
git commit -m "feat: wire reward screen, pause overlay, and ESC/Q controls in main loop"
```

---

## Manual Play-Test Checklist

After all tasks complete, launch the game and verify:

```bash
cd /Users/jamesgale/Documents/zone-survivor && source .venv/bin/activate && python3 main.py
```

- [ ] Game starts with a random weapon (sometimes pistol, sometimes shotgun)
- [ ] Completing room 1 shows reward screen (ROOM CLEAR title, 3 cards)
- [ ] Card 1 is a weapon swap with "Augments reset" footer
- [ ] Cards 2–3 are augments with "Attaches to [weapon]" footer
- [ ] Pressing 1 applies weapon swap — augment slot squares clear in HUD
- [ ] Pressing 2 or 3 applies augment — colored square appears next to weapon name
- [ ] Picking hollow_point on pistol: bullets pierce through enemies, 2nd hit does ~50% damage
- [ ] Picking drum_mag: after reloading, ammo shows doubled (e.g. 12/12 for pistol)
- [ ] Picking fast_loader: reload visibly faster
- [ ] Picking more_pellets on shotgun: visibly more pellets per shot
- [ ] Picking laser_pointer: red aiming line visible, stops at nearest enemy or 300px
- [ ] ESC during ENCOUNTER opens pause overlay (shows upgrades + weapon/augments)
- [ ] ESC during REWARD opens pause overlay
- [ ] Q while paused quits the game
- [ ] ESC while paused resumes
- [ ] Completing room 3 (last room) → WIN screen directly, no reward screen
- [ ] Full run: 3 rooms → WIN
