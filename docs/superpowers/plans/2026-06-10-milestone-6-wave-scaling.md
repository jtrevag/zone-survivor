# Milestone 6 — Wave Scaling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make spawn rate, mutant ratio, and bandit HP scale over time using a minute-based wave table.

**Architecture:** A new `WaveManager` class tracks elapsed game time and exposes current wave parameters as properties. The `Spawner` reads these parameters each tick instead of using static constants. Bandits receive an `hp_mult` at spawn time so HP scaling takes effect on newly spawned enemies only.

**Tech Stack:** Python 3.12, Pygame 2.5+, pytest (new dev dependency)

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `settings.py` | Replace `SPAWN_INTERVAL` with `WAVE_TABLE` |
| Create | `systems/wave_manager.py` | Track elapsed time, expose wave params |
| Create | `tests/test_wave_manager.py` | Unit tests for WaveManager (no pygame needed) |
| Modify | `requirements.txt` | Add pytest |
| Modify | `entities/enemy.py` | `Bandit.__init__` accepts `hp_mult=1.0` |
| Modify | `systems/spawner.py` | Accept `spawn_interval`, `mutant_ratio`, `bandit_hp_mult` |
| Modify | `main.py` | Create `WaveManager`, pass params into spawner each tick |

---

### Task 1: Replace `SPAWN_INTERVAL` with `WAVE_TABLE` in settings.py

**Files:**
- Modify: `settings.py`

- [ ] **Step 1: Write a failing test to confirm the wave table shape**

Create `tests/test_wave_manager.py` with a minimal import check:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import WAVE_TABLE


def test_wave_table_has_five_rows():
    assert len(WAVE_TABLE) == 5


def test_wave_table_row_keys():
    required_keys = {'minute', 'spawn_interval', 'mutant_ratio', 'bandit_hp_mult'}
    for row in WAVE_TABLE:
        assert required_keys.issubset(row.keys())


def test_wave_table_first_row():
    assert WAVE_TABLE[0]['minute'] == 0
    assert WAVE_TABLE[0]['spawn_interval'] == 3.0
    assert WAVE_TABLE[0]['mutant_ratio'] == 0.20
    assert WAVE_TABLE[0]['bandit_hp_mult'] == 1.0
```

- [ ] **Step 2: Add pytest to requirements.txt**

Append to `requirements.txt`:

```
pytest>=8.0
```

File should now read:

```
pygame>=2.5.0
pytest>=8.0
```

Then install:

```bash
source .venv/bin/activate && pip install pytest
```

- [ ] **Step 3: Run the test to verify it fails**

```bash
pytest tests/test_wave_manager.py::test_wave_table_has_five_rows -v
```

Expected: `ERROR` or `FAILED` — `WAVE_TABLE` not found in settings.

- [ ] **Step 5: Add WAVE_TABLE to settings.py and remove SPAWN_INTERVAL**

In `settings.py`, replace this block:

```python
# Spawner
SPAWN_INTERVAL = 3.0      # seconds (wave 0-1 rate)
```

With:

```python
# Wave table — each row activates at the given elapsed-minute mark
WAVE_TABLE = [
    {'minute': 0,  'spawn_interval': 3.0, 'mutant_ratio': 0.20, 'bandit_hp_mult': 1.0},
    {'minute': 2,  'spawn_interval': 2.0, 'mutant_ratio': 0.30, 'bandit_hp_mult': 1.0},
    {'minute': 4,  'spawn_interval': 1.5, 'mutant_ratio': 0.40, 'bandit_hp_mult': 1.2},
    {'minute': 6,  'spawn_interval': 1.0, 'mutant_ratio': 0.50, 'bandit_hp_mult': 1.5},
    {'minute': 10, 'spawn_interval': 0.7, 'mutant_ratio': 0.60, 'bandit_hp_mult': 2.0},
]
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
pytest tests/test_wave_manager.py::test_wave_table_has_five_rows tests/test_wave_manager.py::test_wave_table_row_keys tests/test_wave_manager.py::test_wave_table_first_row -v
```

Expected: 3 PASSED.

- [ ] **Step 7: Commit**

```bash
git add settings.py tests/test_wave_manager.py requirements.txt
git commit -m "feat: replace SPAWN_INTERVAL with WAVE_TABLE in settings"
```

---

### Task 2: Create WaveManager with full unit tests

**Files:**
- Create: `systems/wave_manager.py`
- Modify: `tests/test_wave_manager.py`

- [ ] **Step 1: Add WaveManager tests to test_wave_manager.py**

Append to `tests/test_wave_manager.py` (keep the Task 1 tests at the top):

```python
from systems.wave_manager import WaveManager


def test_initial_params():
    wm = WaveManager()
    assert wm.spawn_interval == 3.0
    assert wm.mutant_ratio == 0.20
    assert wm.bandit_hp_mult == 1.0


def test_minute_2_params():
    wm = WaveManager()
    wm.update(120.0)
    assert wm.spawn_interval == 2.0
    assert wm.mutant_ratio == 0.30
    assert wm.bandit_hp_mult == 1.0


def test_minute_4_params():
    wm = WaveManager()
    wm.update(240.0)
    assert wm.spawn_interval == 1.5
    assert wm.mutant_ratio == 0.40
    assert wm.bandit_hp_mult == 1.2


def test_minute_6_params():
    wm = WaveManager()
    wm.update(360.0)
    assert wm.spawn_interval == 1.0
    assert wm.mutant_ratio == 0.50
    assert wm.bandit_hp_mult == 1.5


def test_minute_10_params():
    wm = WaveManager()
    wm.update(600.0)
    assert wm.spawn_interval == 0.7
    assert wm.mutant_ratio == 0.60
    assert wm.bandit_hp_mult == 2.0


def test_just_before_minute_2_still_at_wave_0():
    wm = WaveManager()
    wm.update(119.9)
    assert wm.spawn_interval == 3.0


def test_past_minute_10_stays_at_max():
    wm = WaveManager()
    wm.update(1200.0)
    assert wm.spawn_interval == 0.7
    assert wm.bandit_hp_mult == 2.0


def test_reset_returns_to_initial():
    wm = WaveManager()
    wm.update(500.0)
    wm.reset()
    assert wm.spawn_interval == 3.0
    assert wm.mutant_ratio == 0.20
    assert wm.bandit_hp_mult == 1.0
```

- [ ] **Step 2: Run to confirm failures**

```bash
pytest tests/test_wave_manager.py -v -k "WaveManager or initial_params or minute"
```

Expected: multiple FAILED — `WaveManager` not defined.

- [ ] **Step 3: Create systems/wave_manager.py**

```python
from settings import WAVE_TABLE


class WaveManager:
    def __init__(self):
        self._elapsed = 0.0

    def update(self, dt):
        self._elapsed += dt

    def reset(self):
        self._elapsed = 0.0

    def _current_row(self):
        minutes = self._elapsed / 60.0
        for row in reversed(WAVE_TABLE):
            if minutes >= row['minute']:
                return row
        return WAVE_TABLE[0]

    @property
    def spawn_interval(self):
        return self._current_row()['spawn_interval']

    @property
    def mutant_ratio(self):
        return self._current_row()['mutant_ratio']

    @property
    def bandit_hp_mult(self):
        return self._current_row()['bandit_hp_mult']
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
pytest tests/test_wave_manager.py -v
```

Expected: 11 PASSED, 0 failed.

- [ ] **Step 5: Commit**

```bash
git add systems/wave_manager.py tests/test_wave_manager.py
git commit -m "feat: add WaveManager with time-based wave param lookup"
```

---

### Task 3: Update Bandit to accept hp_mult

**Files:**
- Modify: `entities/enemy.py:55-66`

The `Bandit` class currently hard-codes `self.hp = BANDIT_MAX_HP`. After this task, it accepts an `hp_mult` float and applies it at init time.

- [ ] **Step 1: Update Bandit.__init__ in entities/enemy.py**

Change lines 55–66 from:

```python
class Bandit(Enemy):
    def __init__(self, pos, all_sprites, enemy_projectiles):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.hp = BANDIT_MAX_HP
        self.xp_value = BANDIT_XP_VALUE
```

To:

```python
class Bandit(Enemy):
    def __init__(self, pos, all_sprites, enemy_projectiles, hp_mult=1.0):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.hp = int(BANDIT_MAX_HP * hp_mult)
        self.xp_value = BANDIT_XP_VALUE
```

- [ ] **Step 2: Verify no test regressions**

```bash
pytest tests/test_wave_manager.py -v
```

Expected: 11 PASSED. (Bandit is pygame-dependent so no direct unit test here — integration verified in Task 6.)

- [ ] **Step 3: Commit**

```bash
git add entities/enemy.py
git commit -m "feat: Bandit accepts hp_mult at spawn time"
```

---

### Task 4: Update Spawner to accept wave parameters

**Files:**
- Modify: `systems/spawner.py`

The spawner currently imports `SPAWN_INTERVAL` from settings (which no longer exists) and uses a fixed `mutant_ratio=0.5` default. After this task it receives all wave params as arguments.

- [ ] **Step 1: Rewrite systems/spawner.py**

Replace the entire file with:

```python
import random
from settings import ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM
from entities.enemy import Mutant, Bandit


class Spawner:
    def __init__(self):
        self._timer = 0.0

    def update(self, dt, all_sprites, enemies, enemy_projectiles,
               spawn_interval, mutant_ratio, bandit_hp_mult=1.0):
        self._timer += dt
        if self._timer >= spawn_interval:
            self._timer -= spawn_interval
            pos = self._random_edge_pos()
            if random.random() < mutant_ratio:
                enemy = Mutant(pos)
            else:
                enemy = Bandit(pos, all_sprites, enemy_projectiles, hp_mult=bandit_hp_mult)
            all_sprites.add(enemy)
            enemies.add(enemy)

    def _random_edge_pos(self):
        return random.choice([
            (random.randint(ARENA_LEFT, ARENA_RIGHT - 1), ARENA_TOP),
            (random.randint(ARENA_LEFT, ARENA_RIGHT - 1), ARENA_BOTTOM),
            (ARENA_LEFT,  random.randint(ARENA_TOP, ARENA_BOTTOM - 1)),
            (ARENA_RIGHT, random.randint(ARENA_TOP, ARENA_BOTTOM - 1)),
        ])
```

- [ ] **Step 2: Run tests to confirm no regressions**

```bash
pytest tests/test_wave_manager.py -v
```

Expected: 11 PASSED.

- [ ] **Step 3: Commit**

```bash
git add systems/spawner.py
git commit -m "feat: Spawner accepts wave params instead of static constants"
```

---

### Task 5: Wire WaveManager into main.py

**Files:**
- Modify: `main.py`

The game loop must create a `WaveManager`, tick it every frame, and pass its current params to `spawner.update()`. On restart, `new_game()` returns a fresh `WaveManager`.

- [ ] **Step 1: Update main.py**

Replace the entire file with:

```python
import pygame
import random
from settings import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES
from entities.player import Player
from entities.xp_orb import XPOrb
from systems.spawner import Spawner
from systems.wave_manager import WaveManager
from ui.hud import HUD


def new_game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    spawner = Spawner()
    wave_manager = WaveManager()
    return player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager


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

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
                    game_over = False
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

        if not game_over and not level_up:
            wave_manager.update(dt)
            all_sprites.update(dt, player)
            spawner.update(
                dt, all_sprites, enemies, enemy_projectiles,
                wave_manager.spawn_interval,
                wave_manager.mutant_ratio,
                wave_manager.bandit_hp_mult,
            )

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

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player)
        if level_up:
            hud.draw_level_up(screen, pending_upgrades, pygame.mouse.get_pos())
        if game_over:
            hud.draw_game_over(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run unit tests one final time**

```bash
pytest tests/test_wave_manager.py -v
```

Expected: 11 PASSED.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: milestone 6 — wave scaling wired into game loop"
```

---

### Task 6: Manual play-test verification

No automated tests for this task — requires visual observation in the running game.

- [ ] **Step 1: Launch the game**

```bash
source .venv/bin/activate && python3 main.py
```

- [ ] **Step 2: Verify wave 0 behaviour (minutes 0–2)**

Enemies spawn roughly every 3 seconds. ~80% are Bandits (blue), ~20% are Mutants (red). Bandits die in 2 shots.

- [ ] **Step 3: Verify wave progression (requires patience or cheat)**

To fast-forward, temporarily change `wave_manager.update(dt)` to `wave_manager.update(dt * 60)` in `main.py`, play 10 seconds of game time (= 10 minutes of wave time), then revert. Observe:
- Enemies spawn noticeably faster
- More Mutants appear in the mix
- Bandits take more hits to kill (wave 4+, hp_mult=1.2 → 96 HP = 3 shots at base 40 damage)

- [ ] **Step 4: Verify restart resets wave**

Die or add a restart. Confirm spawn rate returns to ~3s, Bandit HP returns to 80, ratio returns to 20% Mutants.

- [ ] **Step 5: Revert any debug changes, update CHANGELOG**

In `docs/CHANGELOG.md` add:

```markdown
## Milestone 6 — Wave Scaling

- Added `WaveManager` (`systems/wave_manager.py`) — tracks elapsed time, exposes `spawn_interval`, `mutant_ratio`, `bandit_hp_mult` via wave table lookup
- Replaced static `SPAWN_INTERVAL` constant with `WAVE_TABLE` in `settings.py`
- `Spawner.update()` now accepts wave params per tick instead of using a constant
- `Bandit` accepts `hp_mult` at spawn time — scales HP for waves 4+
- Wave transitions: 0–1 min (3s/20%/1.0×), 2–3 (2s/30%/1.0×), 4–5 (1.5s/40%/1.2×), 6–9 (1s/50%/1.5×), 10+ (0.7s/60%/2.0×)
```

- [ ] **Step 6: Final commit**

```bash
git add docs/CHANGELOG.md
git commit -m "docs: update CHANGELOG for milestone 6 wave scaling"
```

---

### Task 7: SDLC gates — simplify, review, PR

Per CLAUDE.md: simplify → code-review → final play-test → PR. These run after Task 6 play-test is approved.

- [ ] **Step 1: Run /simplify**

```
/simplify
```

Apply any fixes suggested. Commit if changes made:

```bash
git add -p
git commit -m "refactor: simplify wave scaling after review"
```

- [ ] **Step 2: Run /code-review**

```
/code-review
```

Fix any bugs found. Commit if changes made:

```bash
git add -p
git commit -m "fix: code review findings for milestone 6"
```

- [ ] **Step 3: Final play-test checkpoint**

Launch the game and confirm wave scaling still works correctly after any simplify/review fixes. Wait for user sign-off before proceeding.

```bash
source .venv/bin/activate && python3 main.py
```

- [ ] **Step 4: Open PR**

```bash
gh pr create --title "feat: milestone 6 — wave scaling" --body "$(cat <<'EOF'
## Summary
- `WaveManager` tracks elapsed game time and exposes `spawn_interval`, `mutant_ratio`, `bandit_hp_mult` from a wave table
- Spawn rate ramps from 1/3s to 1/0.7s over 10 minutes; Mutant ratio rises from 20% to 60%; Bandit HP scales up to 2× at minute 10
- 11 unit tests cover all wave boundary transitions

## Test plan
- [ ] Game launches without errors
- [ ] Wave 0: ~3s between spawns, mostly Bandits
- [ ] Fast-forward (dt * 60 cheat): spawn rate increases, more Mutants, Bandits tankier
- [ ] Restart resets wave to 0

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-Review

### Spec coverage

| Roadmap requirement | Covered by |
|--------------------|-----------|
| Wave manager ticks on 60s intervals | WaveManager tracks elapsed time; wave row changes at minute boundaries | ✓ |
| Spawn rate increases per wave table | `spawn_interval` varies per row, passed to Spawner each tick | ✓ |
| Mutant ratio increases over time | `mutant_ratio` varies per row, passed to Spawner each tick | ✓ |
| Bandit HP scales after minute 5 | `bandit_hp_mult` 1.2× at minute 4, 1.5× at minute 6 — applied at Bandit init | ✓ |

### Notes

- Existing Bandits keep their HP when a wave transition occurs — only newly spawned Bandits get scaled HP. This is correct game-feel behaviour (no sudden HP jump for enemies already on screen).
- `wave_manager.update(dt)` is called only when `not game_over and not level_up`, so the wave clock pauses during level-up screens and after death. This matches existing spawner pause behaviour.
