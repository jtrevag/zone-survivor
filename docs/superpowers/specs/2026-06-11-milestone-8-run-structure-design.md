# Milestone 8 — Run Structure Design

## Overview

Replace the single 20-minute survival loop with a structured multi-room run. Each room has a type, a completion condition, and a difficulty modifier. Between rooms the player sees a reward screen, then advances. Player stats (HP, XP, level, upgrades) carry across rooms; enemies, projectiles, and XP orbs are cleared.

---

## Room Classes (`systems/run_manager.py`)

Three room types via duck typing — no shared base class.

### `SurviveRoom(duration, difficulty)`
- `update(dt)` — ticks `elapsed`
- `is_complete` — `elapsed >= duration`
- `time_remaining` — `duration - elapsed` (for HUD countdown)
- `mutant_ratio` — `random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)`, set on init
- `difficulty` — float passed to `WaveManager`
- `spawns_waves = True`

### `KillCountRoom(target, difficulty)`
- `record_kill()` — increments `kills`
- `is_complete` — `kills >= target`
- `kills_remaining` — `target - kills` (for HUD)
- `mutant_ratio` — random bounded, set on init
- `difficulty` — float passed to `WaveManager`
- `spawns_waves = True`

### `BossRoom(difficulty)`
- `is_complete` — always `False` (stub until Milestone 11)
- `mutant_ratio` — random bounded, set on init
- `difficulty` — float passed to `WaveManager`
- `spawns_waves = False` — no wave spawning during boss fight

---

## RunManager (`systems/run_manager.py`)

State machine coordinating rooms, wave difficulty, and run-level transitions.

### States
```
ENCOUNTER → ROOM_COMPLETE → REWARD → ENCOUNTER → ... → WIN
                                                      ↗
                                         GAME_OVER (any state)
```

- `ENCOUNTER` — active gameplay; room and wave_manager tick each frame
- `ROOM_COMPLETE` — one-frame state, immediately transitions to `REWARD`
- `REWARD` — "ROOM CLEAR — press R to continue" screen; waits for `advance()`
- `WIN` — final room complete; run won
- `GAME_OVER` — player died

### Interface
```python
RunManager(room_sequence)
  .state              # current state string
  .current_room       # active room object
  .wave_manager       # WaveManager initialised with room's difficulty and mutant_ratio
  .update(dt)         # ticks room + wave_manager; sets state = ROOM_COMPLETE when done
  .record_kill()      # called from main.py on enemy death; delegates to current_room if KillCountRoom
  .advance()          # called from main.py on R press in REWARD; loads next room or WIN
  .on_player_death()  # sets state = GAME_OVER
```

### Room transitions via `advance()`
- Loads next room from sequence, creates new `WaveManager(difficulty, mutant_ratio)`
- Sets state = `ENCOUNTER`
- If no rooms remain, sets state = `WIN`
- Does NOT clear sprites — `main.py` is responsible for that (see below)

---

## WaveManager Changes

`WaveManager.__init__` gains `difficulty=1.0` and `mutant_ratio=0.4` params.

`params` property:
```python
{
    'spawn_interval': self._row.spawn_interval / self.difficulty,
    'hp_mult':        self._row.hp_mult * self.difficulty,
    'mutant_ratio':   self._mutant_ratio,
}
```

`mutant_ratio` removed from `WAVE_TABLE` rows — ratio is now room-owned.

---

## Settings (`settings.py`)

```python
ROOM_MUTANT_RATIO_MIN = 0.2
ROOM_MUTANT_RATIO_MAX = 0.8

ROOM_SEQUENCE = [
    {'type': 'survive',    'duration': 90,  'difficulty': 1.0},
    {'type': 'kill_count', 'target': 25,    'difficulty': 1.4},
    {'type': 'survive',    'duration': 60,  'difficulty': 1.8},
    {'type': 'boss',                        'difficulty': 2.5},
]
```

`Wave` dataclass loses `mutant_ratio` field. All `WAVE_TABLE` rows updated accordingly.

---

## main.py Changes

- Remove `game_over`, `game_won` booleans
- Replace with `run_manager.state` checks: `ENCOUNTER`, `REWARD`, `WIN`, `GAME_OVER`
- On R press in `REWARD` state: clear `enemies`, `enemy_projectiles`, XP orbs from `all_sprites`; call `run_manager.advance()`
- Check `run_manager.current_room.spawns_waves` before calling `spawner.update()` each frame
- Call `run_manager.record_kill()` in main loop when an enemy dies
- `new_game()` constructs `RunManager(ROOM_SEQUENCE)` instead of bare `WaveManager`

---

## HUD Changes

`hud.draw()` signature gains `room` param (replaces bare `elapsed`):

| Room type     | Timer slot shows         |
|---------------|--------------------------|
| `SurviveRoom` | Countdown (`time_remaining`) |
| `KillCountRoom` | "X kills left"         |
| `BossRoom`    | Hidden (M11 adds boss HP bar) |

New overlay: `hud.draw_room_clear(screen)` — same style as existing overlays, shows "ROOM CLEAR" + "Press R to continue".

---

## Carry-Over Between Rooms

| What             | Behaviour          |
|------------------|--------------------|
| Player HP        | Carries            |
| XP + level       | Carries            |
| Upgrades         | Carries            |
| Enemies          | Cleared on advance |
| Enemy projectiles | Cleared on advance |
| XP orbs          | Cleared on advance |

---

## Out of Scope (later milestones)

- Weapon/augment reward cards (Milestone 10)
- Boss room full implementation (Milestone 11)
- Branching room paths (post-v1)
