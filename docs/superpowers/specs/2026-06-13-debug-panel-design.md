# Debug Pause Panel — Design Spec
_2026-06-13_

## Goal

Enable fast iteration on difficulty tuning without restarting the game. Activated via `--debug` CLI flag; zero impact on normal play or WASM builds.

---

## Architecture

Three files change:

| File | Change |
|---|---|
| `main.py` | CLI flag parse, `DebugOverrides` dataclass, debug state vars, pause event handling, spawner call |
| `systems/run_manager.py` | `debug_skip_room()`, `debug_restart_room()` |
| `ui/hud.py` | `draw_debug_panel()` method |

`DebugOverrides` holds live multiplier values. The game loop reads them at spawn time and multiplies onto wave manager params — `settings.py` constants are never mutated. `RunManager` gets two debug-only methods to force state transitions without touching normal game logic.

**WASM safety:** `sys.argv` in the browser is `['main.py']`, so `--debug` is never present. Debug mode stays off with no guard needed.

---

## CLI Flag

```python
import sys
debug_mode = '--debug' in sys.argv
```

Usage: `python3 main.py --debug`

---

## DebugOverrides Dataclass

Defined at module level in `main.py`:

```python
from dataclasses import dataclass

@dataclass
class DebugOverrides:
    spawn_interval_mult: float = 1.0   # range 0.2–3.0, step 0.1  (>1 = slower spawns)
    enemy_hp_mult: float = 1.0         # range 0.1–3.0, step 0.1
```

Instantiated once in `main()`: `debug = DebugOverrides()`. Survives `new_game()` calls — overrides persist across restarts intentionally.

**Enemy speed excluded:** speed is set on the entity at spawn, not passed through the spawner API. Adding it would require a spawner signature change not justified for a debug tool.

---

## Debug Panel UX

The pause menu gains a second view toggled by `D`. State tracked in `main()`:

```python
debug_view: bool = False    # which pause panel is showing
debug_row: int = 0          # selected row (0–4)
```

Panel layout (5 rows):

```
              DEBUG

  ► Spawn interval   ×1.0
    Enemy HP         ×1.0
    [SKIP ROOM]
    [RESTART ROOM]
    [GRANT LEVEL]

    ↑↓ select   ◄► adjust   Enter action
    D  normal pause   ESC  resume
```

- Rows 0–1 are adjustable multipliers; left/right nudges by step.
- Rows 2–4 are actions; Enter executes.
- `D` toggles back to normal pause view.
- `ESC` closes pause entirely (resumes game) from either view.
- Clamping: `spawn_interval_mult` clamps to [0.2, 3.0]; `enemy_hp_mult` clamps to [0.1, 3.0].

---

## Event Handling (main.py)

Added inside the `elif paused:` branch, after the existing ESC/Q checks:

```python
elif debug_mode and event.type == pygame.KEYDOWN:
    if event.key == pygame.K_d:
        debug_view = not debug_view
        debug_row = 0
    elif debug_view:
        if event.key == pygame.K_UP:
            debug_row = (debug_row - 1) % 5
        elif event.key == pygame.K_DOWN:
            debug_row = (debug_row + 1) % 5
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            step = 0.1
            delta = step if event.key == pygame.K_RIGHT else -step
            if debug_row == 0:
                debug.spawn_interval_mult = round(
                    max(0.2, min(3.0, debug.spawn_interval_mult + delta)), 1)
            elif debug_row == 1:
                debug.enemy_hp_mult = round(
                    max(0.1, min(3.0, debug.enemy_hp_mult + delta)), 1)
        elif event.key == pygame.K_RETURN:
            if debug_row == 2:   # SKIP ROOM
                run_manager.debug_skip_room()
                if run_manager.state == 'REWARD':
                    reward_cards = _generate_reward_cards(player)
                paused = False
                debug_view = False
            elif debug_row == 3:  # RESTART ROOM
                for e in list(enemies): e.kill()
                for p in list(enemy_projectiles): p.kill()
                for o in list(xp_orbs): o.kill()
                run_manager.debug_restart_room()
                paused = False
                debug_view = False
            elif debug_row == 4:  # GRANT LEVEL
                player.pending_level_up = True
                paused = False
                debug_view = False
```

---

## Game Loop Integration

Spawner call becomes:

```python
sp_interval = wp['spawn_interval'] * (debug.spawn_interval_mult if debug_mode else 1.0)
sp_hp_mult  = wp['hp_mult']        * (debug.enemy_hp_mult        if debug_mode else 1.0)
spawner.update(dt, all_sprites, enemies, enemy_projectiles,
               spawn_interval=sp_interval,
               mutant_ratio=wp['mutant_ratio'],
               hp_mult=sp_hp_mult)
```

---

## RunManager Additions

Two new methods appended to `RunManager`:

```python
def debug_skip_room(self):
    if self._state != 'ENCOUNTER':
        return
    if self._room_idx >= len(self._sequence) - 1:
        self._state = 'WIN'
    else:
        self._state = 'REWARD'

def debug_restart_room(self):
    if self._state != 'ENCOUNTER':
        return
    self._enter_room(self._sequence[self._room_idx])
```

`debug_skip_room` mirrors the normal completion logic in `update()`. `debug_restart_room` re-enters the current room definition, resetting elapsed/kill_count, and re-rolls mutant ratio.

---

## HUD Addition

New method on `HUD`:

```python
def draw_debug_panel(self, surface, debug, selected_row):
```

Draws the debug overlay on top of the standard pause background. Uses existing font/color infrastructure. Active row highlighted with `►` and a brighter color. Action rows show as `[SKIP ROOM]` etc.; multiplier rows show current value.

No new pre-allocated surfaces needed — debug panel is low-frequency (only shown while paused) so surface caching is not required.

---

## Out of Scope

- Enemy speed multiplier (requires spawner API change)
- Persisting overrides to disk
- Fine-grained per-room objective editing (skip room covers this use case)
- Any debug UI visible during active gameplay
