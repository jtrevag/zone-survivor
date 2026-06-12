# Milestone 8 — Run Structure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single 20-minute survival loop with a structured 3-room run using a `RunManager` state machine.

**Architecture:** Room objects (`SurviveRoom`, `KillCountRoom`, `BossRoom`) own their completion logic and difficulty. `RunManager` drives the state machine (`ENCOUNTER → REWARD → ... → WIN / GAME_OVER`) and owns a `WaveManager` per room. `main.py` replaces `game_over`/`game_won` booleans with `run_manager.state` checks.

**Tech Stack:** Python 3.12, Pygame 2.6, stdlib `unittest`, stdlib `random`

---

## File Map

| File | Change |
|------|--------|
| `settings.py` | Remove `Wave`, `WAVE_TABLE`, `WIN_TIME`; add `BASE_SPAWN_INTERVAL`, `BASE_HP_MULT`, `ROOM_MUTANT_RATIO_MIN/MAX`, `ROOM_SEQUENCE` |
| `systems/wave_manager.py` | Rewrite — stateless params holder; remove `update()`, `elapsed`, `is_complete` |
| `systems/run_manager.py` | **New** — `SurviveRoom`, `KillCountRoom`, `BossRoom`, `RunManager` |
| `ui/hud.py` | Update `draw()` signature; add `draw_room_clear()` |
| `main.py` | Replace booleans with `run_manager.state`; add `xp_orbs` group; SPACE key; `record_kill` |
| `tests/test_wave_manager.py` | Rewrite for new stateless interface |
| `tests/test_win_condition.py` | Delete — obsolete; `WaveManager.is_complete` removed |
| `tests/test_run_manager.py` | **New** — room class + RunManager tests |

---

## Task 1: Simplify WaveManager

**Files:**
- Modify: `settings.py`
- Modify: `systems/wave_manager.py`
- Modify: `tests/test_wave_manager.py`
- Delete: `tests/test_win_condition.py`

- [ ] **Step 1: Replace test_wave_manager.py with failing tests for new interface**

Replace the entire contents of `tests/test_wave_manager.py`:

```python
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWaveManagerParams(unittest.TestCase):
    def test_default_params(self):
        from systems.wave_manager import WaveManager
        from settings import BASE_SPAWN_INTERVAL, BASE_HP_MULT
        wm = WaveManager()
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], BASE_SPAWN_INTERVAL)
        self.assertAlmostEqual(p['hp_mult'], BASE_HP_MULT)
        self.assertAlmostEqual(p['mutant_ratio'], 0.4)

    def test_difficulty_scales_spawn_interval(self):
        from systems.wave_manager import WaveManager
        from settings import BASE_SPAWN_INTERVAL
        wm = WaveManager(difficulty=2.0, mutant_ratio=0.5)
        self.assertAlmostEqual(wm.params['spawn_interval'], BASE_SPAWN_INTERVAL / 2.0)

    def test_difficulty_scales_hp_mult(self):
        from systems.wave_manager import WaveManager
        from settings import BASE_HP_MULT
        wm = WaveManager(difficulty=2.0, mutant_ratio=0.5)
        self.assertAlmostEqual(wm.params['hp_mult'], BASE_HP_MULT * 2.0)

    def test_mutant_ratio_stored(self):
        from systems.wave_manager import WaveManager
        wm = WaveManager(difficulty=1.0, mutant_ratio=0.7)
        self.assertAlmostEqual(wm.params['mutant_ratio'], 0.7)

    def test_params_returns_new_dict_each_call(self):
        from systems.wave_manager import WaveManager
        wm = WaveManager()
        self.assertIsNot(wm.params, wm.params)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run to confirm new tests fail**

```bash
source .venv/bin/activate && python -m unittest tests/test_wave_manager.py -v
```

Expected: `ImportError` or `AttributeError` — `BASE_SPAWN_INTERVAL` not defined yet.

- [ ] **Step 3: Delete test_win_condition.py**

```bash
rm tests/test_win_condition.py
```

- [ ] **Step 4: Update settings.py — remove wave table, add base constants**

Remove from `settings.py`:
- `@dataclass(frozen=True)` block for `Wave`
- The entire `WAVE_TABLE` list
- `WIN_TIME = 1200.0`

Add after the `SOUND_BUFFER_SIZE` line:

```python
# Wave difficulty base values (scaled per room by difficulty multiplier)
BASE_SPAWN_INTERVAL = 2.0   # seconds between spawns at difficulty 1.0
BASE_HP_MULT = 1.0           # enemy HP multiplier at difficulty 1.0
```

- [ ] **Step 5: Rewrite systems/wave_manager.py**

Replace entire file:

```python
from settings import BASE_SPAWN_INTERVAL, BASE_HP_MULT


class WaveManager:
    def __init__(self, difficulty=1.0, mutant_ratio=0.4):
        self._difficulty = difficulty
        self._mutant_ratio = mutant_ratio

    @property
    def params(self):
        return {
            'spawn_interval': BASE_SPAWN_INTERVAL / self._difficulty,
            'hp_mult':        BASE_HP_MULT * self._difficulty,
            'mutant_ratio':   self._mutant_ratio,
        }
```

- [ ] **Step 6: Run tests to confirm they pass**

```bash
source .venv/bin/activate && python -m unittest tests/test_wave_manager.py -v
```

Expected: 5 tests pass.

- [ ] **Step 7: Run full suite to confirm no regressions**

```bash
source .venv/bin/activate && python -m unittest discover tests/ -v
```

Expected: All pass. `test_win_condition` tests are gone. `test_wave_manager` runs 5 new tests.

- [ ] **Step 8: Commit**

```bash
git add settings.py systems/wave_manager.py tests/test_wave_manager.py tests/test_win_condition.py
git commit -m "refactor: replace WAVE_TABLE with per-room difficulty multiplier"
```

---

## Task 2: Room Classes

**Files:**
- Create: `systems/run_manager.py`
- Modify: `settings.py`
- Create: `tests/test_run_manager.py`

- [ ] **Step 1: Add room ratio constants to settings.py**

Add after `BASE_HP_MULT`:

```python
# Per-room mutant spawn ratio (randomised within this range each room)
ROOM_MUTANT_RATIO_MIN = 0.2
ROOM_MUTANT_RATIO_MAX = 0.8
```

- [ ] **Step 2: Write failing tests for room classes**

Create `tests/test_run_manager.py`:

```python
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSurviveRoom(unittest.TestCase):
    def _make(self, duration=90, difficulty=1.0):
        from systems.run_manager import SurviveRoom
        return SurviveRoom(duration, difficulty)

    def test_not_complete_initially(self):
        r = self._make()
        self.assertFalse(r.is_complete)

    def test_complete_after_duration(self):
        r = self._make(duration=90)
        r.update(90.1)
        self.assertTrue(r.is_complete)

    def test_not_complete_just_before_duration(self):
        r = self._make(duration=90)
        r.update(89.9)
        self.assertFalse(r.is_complete)

    def test_time_remaining(self):
        r = self._make(duration=90)
        r.update(30)
        self.assertAlmostEqual(r.time_remaining, 60.0)

    def test_timer_display_shows_seconds(self):
        r = self._make(duration=90)
        r.update(30)
        self.assertEqual(r.timer_display, '60s')

    def test_spawns_waves(self):
        r = self._make()
        self.assertTrue(r.spawns_waves)

    def test_mutant_ratio_within_bounds(self):
        from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
        for _ in range(20):
            r = self._make()
            self.assertGreaterEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MIN)
            self.assertLessEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MAX)

    def test_difficulty_stored(self):
        r = self._make(difficulty=1.8)
        self.assertAlmostEqual(r.difficulty, 1.8)


class TestKillCountRoom(unittest.TestCase):
    def _make(self, target=25, difficulty=1.4):
        from systems.run_manager import KillCountRoom
        return KillCountRoom(target, difficulty)

    def test_not_complete_initially(self):
        r = self._make()
        self.assertFalse(r.is_complete)

    def test_complete_at_target(self):
        r = self._make(target=3)
        r.record_kill()
        r.record_kill()
        r.record_kill()
        self.assertTrue(r.is_complete)

    def test_not_complete_before_target(self):
        r = self._make(target=3)
        r.record_kill()
        r.record_kill()
        self.assertFalse(r.is_complete)

    def test_kills_remaining(self):
        r = self._make(target=25)
        r.record_kill()
        self.assertEqual(r.kills_remaining, 24)

    def test_timer_display_shows_kills_remaining(self):
        r = self._make(target=25)
        r.record_kill()
        self.assertEqual(r.timer_display, '24 kills left')

    def test_spawns_waves(self):
        r = self._make()
        self.assertTrue(r.spawns_waves)

    def test_mutant_ratio_within_bounds(self):
        from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
        for _ in range(20):
            r = self._make()
            self.assertGreaterEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MIN)
            self.assertLessEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MAX)


class TestBossRoom(unittest.TestCase):
    def _make(self, difficulty=2.5):
        from systems.run_manager import BossRoom
        return BossRoom(difficulty)

    def test_never_complete(self):
        r = self._make()
        self.assertFalse(r.is_complete)

    def test_no_wave_spawning(self):
        r = self._make()
        self.assertFalse(r.spawns_waves)

    def test_timer_display_is_none(self):
        r = self._make()
        self.assertIsNone(r.timer_display)

    def test_mutant_ratio_within_bounds(self):
        from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
        for _ in range(20):
            r = self._make()
            self.assertGreaterEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MIN)
            self.assertLessEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MAX)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 3: Run to confirm tests fail**

```bash
source .venv/bin/activate && python -m unittest tests/test_run_manager.py -v
```

Expected: `ModuleNotFoundError: No module named 'systems.run_manager'`

- [ ] **Step 4: Create systems/run_manager.py with room classes**

```python
import random
from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX


class SurviveRoom:
    spawns_waves = True

    def __init__(self, duration, difficulty):
        self.duration = duration
        self.difficulty = difficulty
        self.mutant_ratio = random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)
        self._elapsed = 0.0

    def update(self, dt):
        self._elapsed += dt

    @property
    def is_complete(self):
        return self._elapsed >= self.duration

    @property
    def time_remaining(self):
        return max(0.0, self.duration - self._elapsed)

    @property
    def timer_display(self):
        return f'{int(self.time_remaining)}s'


class KillCountRoom:
    spawns_waves = True

    def __init__(self, target, difficulty):
        self.target = target
        self.difficulty = difficulty
        self.mutant_ratio = random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)
        self._kills = 0

    def record_kill(self):
        self._kills += 1

    @property
    def is_complete(self):
        return self._kills >= self.target

    @property
    def kills_remaining(self):
        return max(0, self.target - self._kills)

    @property
    def timer_display(self):
        return f'{self.kills_remaining} kills left'


class BossRoom:
    spawns_waves = False

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.mutant_ratio = random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)

    @property
    def is_complete(self):
        return False

    @property
    def timer_display(self):
        return None
```

- [ ] **Step 5: Run room class tests**

```bash
source .venv/bin/activate && python -m unittest tests/test_run_manager.py -v
```

Expected: All room tests pass.

- [ ] **Step 6: Commit**

```bash
git add settings.py systems/run_manager.py tests/test_run_manager.py
git commit -m "feat: add room classes (SurviveRoom, KillCountRoom, BossRoom)"
```

---

## Task 3: RunManager State Machine

**Files:**
- Modify: `systems/run_manager.py` (append `RunManager` class)
- Modify: `settings.py` (add `ROOM_SEQUENCE`)
- Modify: `tests/test_run_manager.py` (append RunManager tests)

- [ ] **Step 1: Add ROOM_SEQUENCE to settings.py**

Add after `ROOM_MUTANT_RATIO_MAX`:

```python
# Room sequence for a full run (boss room added in Milestone 11)
ROOM_SEQUENCE = [
    {'type': 'survive',    'duration': 90,  'difficulty': 1.0},
    {'type': 'kill_count', 'target': 25,    'difficulty': 1.4},
    {'type': 'survive',    'duration': 60,  'difficulty': 1.8},
]
```

- [ ] **Step 2: Append failing RunManager tests to tests/test_run_manager.py**

Add this class at the bottom of `tests/test_run_manager.py` (before `if __name__ == '__main__':`):

```python
class TestRunManager(unittest.TestCase):
    def _sequence(self):
        return [
            {'type': 'survive', 'duration': 90, 'difficulty': 1.0},
            {'type': 'survive', 'duration': 60, 'difficulty': 1.8},
        ]

    def _make(self, sequence=None):
        from systems.run_manager import RunManager
        return RunManager(sequence if sequence is not None else self._sequence())

    def test_starts_in_encounter(self):
        rm = self._make()
        self.assertEqual(rm.state, 'ENCOUNTER')

    def test_empty_sequence_wins_immediately(self):
        rm = self._make([])
        self.assertEqual(rm.state, 'WIN')

    def test_current_room_is_first_room(self):
        from systems.run_manager import SurviveRoom
        rm = self._make()
        self.assertIsInstance(rm.current_room, SurviveRoom)

    def test_wave_manager_initialised_with_room_difficulty(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.8}])
        self.assertAlmostEqual(rm.wave_manager._difficulty, 1.8)

    def test_wave_manager_initialised_with_room_mutant_ratio(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.0}])
        self.assertAlmostEqual(rm.wave_manager._mutant_ratio, rm.current_room.mutant_ratio)

    def test_transitions_to_reward_when_room_complete(self):
        rm = self._make([{'type': 'survive', 'duration': 1, 'difficulty': 1.0}])
        rm.update(1.1)
        self.assertEqual(rm.state, 'REWARD')

    def test_does_not_complete_before_duration(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.0}])
        rm.update(89.9)
        self.assertEqual(rm.state, 'ENCOUNTER')

    def test_advance_loads_next_room(self):
        from systems.run_manager import SurviveRoom
        seq = [
            {'type': 'survive',    'duration': 1,  'difficulty': 1.0},
            {'type': 'survive',    'duration': 60, 'difficulty': 1.8},
        ]
        rm = self._make(seq)
        rm.update(1.1)  # room 1 completes → REWARD
        rm.advance()
        self.assertEqual(rm.state, 'ENCOUNTER')
        self.assertAlmostEqual(rm.current_room.duration, 60)

    def test_advance_on_last_room_sets_win(self):
        rm = self._make([{'type': 'survive', 'duration': 1, 'difficulty': 1.0}])
        rm.update(1.1)
        rm.advance()
        self.assertEqual(rm.state, 'WIN')

    def test_player_death_sets_game_over(self):
        rm = self._make()
        rm.on_player_death()
        self.assertEqual(rm.state, 'GAME_OVER')

    def test_run_elapsed_accumulates(self):
        rm = self._make()
        rm.update(1.0)
        rm.update(2.0)
        self.assertAlmostEqual(rm.run_elapsed, 3.0)

    def test_run_elapsed_pauses_in_reward(self):
        rm = self._make([{'type': 'survive', 'duration': 1, 'difficulty': 1.0}])
        rm.update(1.1)   # → REWARD; run_elapsed = 1.1
        elapsed_at_reward = rm.run_elapsed
        rm.update(5.0)   # REWARD state — should not tick elapsed
        self.assertAlmostEqual(rm.run_elapsed, elapsed_at_reward)

    def test_record_kill_delegates_to_kill_count_room(self):
        rm = self._make([{'type': 'kill_count', 'target': 1, 'difficulty': 1.0}])
        rm.record_kill()
        rm.update(0.0)
        self.assertEqual(rm.state, 'REWARD')

    def test_record_kill_ignored_for_survive_room(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.0}])
        rm.record_kill()  # should not raise
        self.assertEqual(rm.state, 'ENCOUNTER')

    def test_kill_count_room_built_from_sequence(self):
        from systems.run_manager import KillCountRoom
        rm = self._make([{'type': 'kill_count', 'target': 25, 'difficulty': 1.4}])
        self.assertIsInstance(rm.current_room, KillCountRoom)
        self.assertEqual(rm.current_room.target, 25)
```

- [ ] **Step 3: Run to confirm new tests fail**

```bash
source .venv/bin/activate && python -m unittest tests/test_run_manager.py::TestRunManager -v 2>&1 | head -20
```

Expected: `AttributeError` — `RunManager` not defined yet.

- [ ] **Step 4: Append RunManager to systems/run_manager.py**

First, add the WaveManager import to the top of the file. The top of `systems/run_manager.py` currently reads:
```python
import random
from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
```
Change it to:
```python
import random
from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
from systems.wave_manager import WaveManager
```

Then add the `RunManager` class after `BossRoom`:

```python
class RunManager:
    def __init__(self, room_sequence):
        self._sequence = list(room_sequence)
        self._room_idx = 0
        self._run_elapsed = 0.0
        if not self._sequence:
            self._state = 'WIN'
            self._current_room = None
            self._wave_manager = None
        else:
            self._state = 'ENCOUNTER'
            self._current_room = self._build_room(self._sequence[0])
            self._wave_manager = WaveManager(
                difficulty=self._current_room.difficulty,
                mutant_ratio=self._current_room.mutant_ratio,
            )

    def _build_room(self, defn):
        t = defn['type']
        d = defn['difficulty']
        if t == 'survive':
            return SurviveRoom(defn['duration'], d)
        if t == 'kill_count':
            return KillCountRoom(defn['target'], d)
        return BossRoom(d)

    @property
    def state(self):
        return self._state

    @property
    def current_room(self):
        return self._current_room

    @property
    def wave_manager(self):
        return self._wave_manager

    @property
    def run_elapsed(self):
        return self._run_elapsed

    def update(self, dt):
        if self._state != 'ENCOUNTER':
            return
        self._run_elapsed += dt
        self._current_room.update(dt)
        if self._current_room.is_complete:
            self._state = 'REWARD'

    def record_kill(self):
        if self._state != 'ENCOUNTER':
            return
        if isinstance(self._current_room, KillCountRoom):
            self._current_room.record_kill()

    def advance(self):
        self._room_idx += 1
        if self._room_idx >= len(self._sequence):
            self._state = 'WIN'
            return
        self._current_room = self._build_room(self._sequence[self._room_idx])
        self._wave_manager = WaveManager(
            difficulty=self._current_room.difficulty,
            mutant_ratio=self._current_room.mutant_ratio,
        )
        self._state = 'ENCOUNTER'

    def on_player_death(self):
        self._state = 'GAME_OVER'
```

**Note:** The `from systems.wave_manager import WaveManager` import must go at the top of the file (after the existing `import random` and `from settings import ...` lines), not inside the class. Move it there.

- [ ] **Step 5: Run all run_manager tests**

```bash
source .venv/bin/activate && python -m unittest tests/test_run_manager.py -v
```

Expected: All tests pass.

- [ ] **Step 6: Run full suite**

```bash
source .venv/bin/activate && python -m unittest discover tests/ -v
```

Expected: All pass.

- [ ] **Step 7: Commit**

```bash
git add settings.py systems/run_manager.py tests/test_run_manager.py
git commit -m "feat: add RunManager state machine and ROOM_SEQUENCE"
```

---

## Task 4: HUD Updates

**Files:**
- Modify: `ui/hud.py`

- [ ] **Step 1: Update `draw()` signature and timer logic**

In `ui/hud.py`, replace the entire `draw` method signature and timer block (lines 92–102):

```python
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
```

with:

```python
def draw(self, surface, player, room=None):
    # Timer — top-center (text supplied by room; None hides it)
    if room is not None and room.timer_display is not None:
        timer_text = room.timer_display
        if timer_text != self._cached_elapsed_sec:
            self._timer_surf, _ = self._font.render(timer_text, HUD_COLOR_AMMO)
            self._cached_elapsed_sec = timer_text
        surface.blit(self._timer_surf, (
            (WIDTH - self._timer_surf.get_width()) // 2,
            HUD_MARGIN,
        ))
```

- [ ] **Step 2: Add `draw_room_clear` overlay method**

Append after `draw_win_screen` (after line 189):

```python
def draw_room_clear(self, surface):
    self._overlay_surf.fill((0, 0, 0, 160))
    title_surf, title_rect = self._font_large.render('ROOM CLEAR', (220, 220, 220))
    self._overlay_surf.blit(title_surf, (
        (WIDTH - title_rect.width) // 2,
        HEIGHT // 2 - 60,
    ))
    sub_surf, sub_rect = self._font.render('Press SPACE to continue', (160, 160, 160))
    self._overlay_surf.blit(sub_surf, (
        (WIDTH - sub_rect.width) // 2,
        HEIGHT // 2 + 10,
    ))
    surface.blit(self._overlay_surf, (0, 0))
```

- [ ] **Step 3: Verify HUD renders by launching game briefly**

```bash
source .venv/bin/activate && python3 main.py
```

Expected: Crash or visible error because `main.py` still passes `wave_manager.elapsed` to `hud.draw()`. That's expected — fixed in Task 5.

- [ ] **Step 4: Commit**

```bash
git add ui/hud.py
git commit -m "feat: update HUD for per-room timer and room-clear overlay"
```

---

## Task 5: main.py Integration

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Update imports in main.py**

Replace:
```python
from systems.wave_manager import WaveManager
```
with:
```python
from systems.run_manager import RunManager
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES,
    HIT_FLASH_COLOR, HIT_FLASH_DURATION, HIT_FLASH_ALPHA_MAX,
    SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE,
    ROOM_SEQUENCE,
)
```

- [ ] **Step 2: Rewrite new_game()**

Replace the existing `new_game()` function:

```python
def new_game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    xp_orbs = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    spawner = Spawner()
    run_manager = RunManager(ROOM_SEQUENCE)
    return player, all_sprites, enemies, bullets, enemy_projectiles, xp_orbs, spawner, run_manager
```

- [ ] **Step 3: Update the call sites for new_game()**

Replace the initial call:
```python
player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
game_over = False
game_won = False
level_up = False
pending_upgrades = []
```
with:
```python
player, all_sprites, enemies, bullets, enemy_projectiles, xp_orbs, spawner, run_manager = new_game()
level_up = False
pending_upgrades = []
```

- [ ] **Step 4: Rewrite the event handling block**

Replace the entire `for event in pygame.event.get():` block:

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
        running = False
    elif run_manager.state in ('WIN', 'GAME_OVER'):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            player, all_sprites, enemies, bullets, enemy_projectiles, xp_orbs, spawner, run_manager = new_game()
            level_up = False
            pending_upgrades = []
    elif run_manager.state == 'REWARD':
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            for e in list(enemies): e.kill()
            for p in list(enemy_projectiles): p.kill()
            for o in list(xp_orbs): o.kill()
            run_manager.advance()
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
    else:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            player.try_reload()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            bullet = player.try_fire()
            if bullet:
                all_sprites.add(bullet)
                bullets.add(bullet)
                sounds.play_gunshot()
```

- [ ] **Step 5: Rewrite the gameplay update block**

Replace:
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

with:

```python
if run_manager.state == 'ENCOUNTER' and not level_up:
    run_manager.update(dt)
    all_sprites.update(dt, player)
    if run_manager.current_room.spawns_waves:
        wp = run_manager.wave_manager.params
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
                xp_orbs.add(orb)
                run_manager.record_kill()

    for proj in pygame.sprite.spritecollide(player, enemy_projectiles, True):
        player.take_damage(proj.damage)

    if player.just_hit:
        sounds.play_hit()
        player.just_hit = False
    if player.reload_complete:
        sounds.play_reload()
        player.reload_complete = False

    if player.dead:
        run_manager.on_player_death()
        sounds.play_death()
    elif player.pending_level_up:
        player.pending_level_up = False
        level_up = True
        pending_upgrades = random.sample(UPGRADES, 3)
```

- [ ] **Step 6: Update the draw/overlay section**

Replace:
```python
hud.draw(screen, player, wave_manager.elapsed)
...
if game_over:
    hud.draw_game_over(screen, wave_manager.elapsed)
if game_won:
    hud.draw_win_screen(screen, wave_manager.elapsed)
```

with:

```python
hud.draw(screen, player, run_manager.current_room)
...
if run_manager.state == 'REWARD':
    hud.draw_room_clear(screen)
if run_manager.state == 'GAME_OVER':
    hud.draw_game_over(screen, run_manager.run_elapsed)
if run_manager.state == 'WIN':
    hud.draw_win_screen(screen, run_manager.run_elapsed)
```

- [ ] **Step 7: Launch the game and play-test**

```bash
source .venv/bin/activate && python3 main.py
```

Verify:
- Game starts; enemies spawn; shooting, reload, XP leveling all work
- Survive room countdown shows in HUD (e.g. "90s")
- After 90s, "ROOM CLEAR / Press SPACE" overlay appears; game pauses
- SPACE clears enemies and advances to kill-count room; HUD shows "25 kills left"
- Kill 25 enemies; "ROOM CLEAR" appears again
- SPACE advances to final survive room (60s countdown)
- Complete final room; SPACE → WIN screen
- Player death → GAME OVER screen; R restarts
- Level-up screen still works mid-room

- [ ] **Step 8: Run full test suite**

```bash
source .venv/bin/activate && python -m unittest discover tests/ -v
```

Expected: All tests pass.

- [ ] **Step 9: Commit**

```bash
git add main.py
git commit -m "feat: milestone 8 — run structure with RunManager state machine"
```

---

## Task 6: Update CHANGELOG and ROADMAP

**Files:**
- Modify: `docs/CHANGELOG.md`
- Modify: `docs/ROADMAP.md`

- [ ] **Step 1: Update CHANGELOG.md**

Add entry at the top:

```markdown
## Milestone 8 — Run Structure

- Added `RunManager` state machine: `ENCOUNTER → REWARD → ... → WIN / GAME_OVER`
- Added `SurviveRoom`, `KillCountRoom`, `BossRoom` room classes with per-room difficulty
- Replaced `WAVE_TABLE` with `BASE_SPAWN_INTERVAL`/`BASE_HP_MULT` + per-room difficulty multiplier
- Mutant ratio now randomised per room (`ROOM_MUTANT_RATIO_MIN/MAX`) instead of time-based ramp
- Added dedicated `xp_orbs` sprite group; enemies, projectiles, and orbs cleared between rooms
- HUD timer shows per-room countdown (survive) or kills remaining (kill count)
- SPACE advances from reward screen; R key reserved for reload
```

- [ ] **Step 2: Mark Milestone 8 complete in ROADMAP.md**

Check off all items under `## Milestone 8 — Run Structure` and update the ROADMAP note on `WaveManager`:

Change:
```markdown
- [ ] `WaveManager` accepts `time_offset` param — initialises `self.elapsed = time_offset`
```
to:
```markdown
- [x] `WaveManager` simplified — stateless params holder; difficulty float replaces `time_offset`
```

Mark remaining items complete.

- [ ] **Step 3: Commit**

```bash
git add docs/CHANGELOG.md docs/ROADMAP.md
git commit -m "docs: record milestone 8 in changelog and roadmap"
```
