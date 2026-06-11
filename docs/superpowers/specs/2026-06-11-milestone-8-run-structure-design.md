# Milestone 8 — Run Structure Design

## Overview

Replace the single 20-minute survival loop with a structured multi-room run. Each room has a type, a completion condition, and a difficulty modifier. Difficulty is per-room only — no time-based escalation within a room. Between rooms the player sees a reward screen, then advances with SPACE. Player stats (HP, XP, level, upgrades) carry across rooms; enemies, projectiles, and XP orbs are cleared.

> **ROADMAP note:** The ROADMAP spec for M8 describes a `time_offset` param on `WaveManager`. This design supersedes that — difficulty is a direct float multiplier, not a fake elapsed-time offset. `WAVE_TABLE` is removed entirely.

---

## Room Classes (`systems/run_manager.py`)

Three room types via duck typing — no shared base class.

### `SurviveRoom(duration, difficulty)`
- `update(dt)` — ticks `elapsed`
- `is_complete` — `elapsed >= duration`
- `time_remaining` — `duration - elapsed` (for HUD countdown)
- `mutant_ratio` — `random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)`, set on init
- `difficulty` — float, passed to `WaveManager`
- `spawns_waves = True`

### `KillCountRoom(target, difficulty)`
- `record_kill()` — increments `kills`
- `is_complete` — `kills >= target`
- `kills_remaining` — `target - kills` (for HUD)
- `mutant_ratio` — random bounded, set on init
- `difficulty` — float, passed to `WaveManager`
- `spawns_waves = True`

### `BossRoom(difficulty)`
- `is_complete` — always `False` (stub until Milestone 11)
- `mutant_ratio` — random bounded, set on init
- `difficulty` — float, passed to `WaveManager`
- `spawns_waves = False` — no wave spawning during boss fight

`BossRoom` is defined but not included in `ROOM_SEQUENCE` until Milestone 11 — keeping it out ensures `WIN` is reachable in M8.

---

## RunManager (`systems/run_manager.py`)

State machine coordinating rooms, wave difficulty, and run-level transitions.

### States
```
ENCOUNTER → ROOM_COMPLETE → REWARD → ENCOUNTER → ... → WIN
                                                      ↗
                                         GAME_OVER (any state)
```

- `ENCOUNTER` — active gameplay; room ticks each frame
- `ROOM_COMPLETE` — one-frame state, immediately transitions to `REWARD`
- `REWARD` — "ROOM CLEAR — press SPACE to continue" screen; gameplay paused; waits for `advance()`
- `WIN` — final room complete; run won
- `GAME_OVER` — player died

### Interface
```python
RunManager(room_sequence)
  .state              # current state string
  .current_room       # active room object (set in __init__; empty sequence → WIN immediately)
  .wave_manager       # WaveManager initialised with room's difficulty and mutant_ratio
  .run_elapsed        # total seconds across all rooms (for end screens)
  .update(dt)         # ticks run_elapsed + current_room; sets state = ROOM_COMPLETE when done
  .record_kill()      # called from main.py on enemy death; delegates to current_room if KillCountRoom
  .advance()          # called on SPACE in REWARD; loads next room or sets WIN
  .on_player_death()  # sets state = GAME_OVER
```

### Constructor behaviour
- `__init__` loads the first room from `room_sequence` into `current_room` and creates its `WaveManager`
- If `room_sequence` is empty, state is set to `WIN` immediately

### Room transitions via `advance()`
- Loads next room from sequence, creates new `WaveManager(difficulty, mutant_ratio)`
- Sets state = `ENCOUNTER`
- If no rooms remain, sets state = `WIN`
- Does NOT clear sprites — `main.py` owns that (see below)

### State priority in main loop
- Check `pending_level_up` before checking `run_manager.state == ROOM_COMPLETE` — level-up screen takes priority if both trigger on the same frame

---

## WaveManager Changes

`WAVE_TABLE`, `WIN_TIME`, and `is_complete` are removed. WaveManager becomes a stateless params holder.

`WaveManager.__init__(difficulty=1.0, mutant_ratio=0.4)` — stores both; no elapsed tracking.

`params` property:
```python
{
    'spawn_interval': BASE_SPAWN_INTERVAL / self.difficulty,
    'hp_mult':        BASE_HP_MULT * self.difficulty,
    'mutant_ratio':   self._mutant_ratio,
}
```

`update(dt)` is removed — no time-based escalation.

---

## Settings (`settings.py`)

Removed: `Wave` dataclass, `WAVE_TABLE`, `WIN_TIME`.

Added:
```python
BASE_SPAWN_INTERVAL = 2.0   # seconds between spawns at difficulty 1.0
BASE_HP_MULT = 1.0           # enemy HP multiplier at difficulty 1.0

ROOM_MUTANT_RATIO_MIN = 0.2
ROOM_MUTANT_RATIO_MAX = 0.8

ROOM_SEQUENCE = [
    {'type': 'survive',    'duration': 90,  'difficulty': 1.0},
    {'type': 'kill_count', 'target': 25,    'difficulty': 1.4},
    {'type': 'survive',    'duration': 60,  'difficulty': 1.8},
]
```

---

## main.py Changes

- Remove `game_over`, `game_won` booleans
- Replace with `run_manager.state` checks: `ENCOUNTER`, `REWARD`, `WIN`, `GAME_OVER`
- On SPACE press in `REWARD` state: clear `enemies`, `enemy_projectiles`, `xp_orbs` groups; call `run_manager.advance()`
- During `REWARD` state: skip `all_sprites.update()` and `spawner.update()` — gameplay paused
- Check `run_manager.current_room.spawns_waves` before calling `spawner.update()` in `ENCOUNTER`
- Call `run_manager.record_kill()` when an enemy dies
- `new_game()` constructs `RunManager(ROOM_SEQUENCE)` instead of bare `WaveManager`
- Add dedicated `xp_orbs = pygame.sprite.Group()` in `new_game()` — orbs added to both `all_sprites` and `xp_orbs`
- End screens (`draw_game_over`, `draw_win_screen`) read `run_manager.run_elapsed` for time survived

---

## HUD Changes

`hud.draw()` gains `room` param (replaces bare `elapsed`):

| Room type       | Timer slot shows              |
|-----------------|-------------------------------|
| `SurviveRoom`   | Countdown (`time_remaining`)  |
| `KillCountRoom` | "X kills left"                |
| `BossRoom`      | Hidden (M11 adds boss HP bar) |

New overlay: `hud.draw_room_clear(screen)` — same style as existing overlays, shows "ROOM CLEAR" + "Press SPACE to continue".

---

## Carry-Over Between Rooms

| What              | Behaviour          |
|-------------------|--------------------|
| Player HP         | Carries            |
| XP + level        | Carries            |
| Upgrades          | Carries            |
| Enemies           | Cleared on advance |
| Enemy projectiles | Cleared on advance |
| XP orbs           | Cleared on advance |
| Bullets           | Cleared on advance |

---

## Out of Scope (later milestones)

- Weapon/augment reward cards (Milestone 10)
- Boss room full implementation — `BossRoom.is_complete`, boss spawning (Milestone 11)
- Branching room paths (post-v1)
