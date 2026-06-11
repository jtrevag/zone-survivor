# Run Structure, Weapons & Augments — Design Spec
> Date: 2026-06-11 | Status: Approved

## Overview

Replace the current 20-minute survival loop with a sequential room system. Add a second weapon (shotgun) and a weapon augment system. Two distinct reward tiers keep level-up pickups small and room-complete pickups big.

This is a skeleton — room count, weapons, and augments expand in future milestones. The map/branching-path structure (Slay the Spire style) is a future milestone; this iteration is linear.

---

## 1. Run Structure

### States

```
ENCOUNTER → ROOM_COMPLETE → REWARD → ENCOUNTER → ... → BOSS_ENCOUNTER → BOSS_COMPLETE → WIN
```

### RunManager (`systems/run_manager.py`)

New system class. Owns:
- `room_sequence` — list of room defs loaded from `settings.py`
- `current_room_index` — int
- `state` — enum: `ENCOUNTER`, `ROOM_COMPLETE`, `REWARD`, `WIN`, `GAME_OVER`
- `kill_count` — incremented by `main.py` on enemy death
- Room completion logic per type

`main.py` calls `run_manager.update(dt)` each frame. Reads `run_manager.state` to decide what to render. `game_over` and `game_won` flags replaced by `run_manager.state`.

### Room Types

| Type | Complete condition |
|------|--------------------|
| `survive` | `elapsed >= duration` |
| `kill_count` | `kill_count >= target` |
| `boss` | all boss entities dead |

### Room Sequence (configurable in `settings.py`)

3 rooms + boss:
```python
ROOM_SEQUENCE = [
    {"type": "survive",    "duration": 60,  "difficulty": 1},
    {"type": "kill_count", "target":  25,   "difficulty": 2},
    {"type": "survive",    "duration": 90,  "difficulty": 3},
    {"type": "boss",                        "difficulty": 4},
]
```

### Difficulty Scaling Per Room

Each room passes its `difficulty` value to `WaveManager` as a time offset. `WaveManager` receives a `time_offset` param (seconds) so it starts evaluating `WAVE_TABLE` from mid-table rather than from minute 0. Room difficulty maps to offset: `time_offset = (difficulty - 1) * 60`. `WaveManager.__init__` accepts `time_offset=0` and initialises `self.elapsed = time_offset`.

### Room Reset

Between rooms: all enemies, projectiles, and XP orbs cleared. Player HP and weapon carry over. `WaveManager` reinitialised at new difficulty tier.

---

## 2. Weapons

### Weapon as Data

Player stats related to weapons (`mag_size`, `reload_time`, `damage`, `shot_cooldown_base`) move from hardcoded constants into a weapon definition object. Player holds `self.weapon` (a dict) and `self.augments` (list, max 2).

`Player.equip(weapon_def)` sets `self.weapon`, resets ammo, clears augments.

### Weapon Definitions (`settings.py`)

```python
WEAPONS = {
    "bolt_action": {
        "name": "Bolt-Action Rifle",
        "mag": 5,
        "reload": 2.0,
        "damage": 40,
        "cooldown": 0.4,
        "pellets": 1,
        "spread": 0,
        "bullet_radius": 6,
        "bullet_shape": "rect",   # elongated, rotated to velocity direction
        "bullet_color": YELLOW,
    },
    "shotgun": {
        "name": "Shotgun",
        "mag": 2,
        "reload": 2.5,
        "damage": 15,
        "cooldown": 0.6,
        "pellets": 4,
        "spread": 25,             # degrees, cone half-angle
        "bullet_radius": 2,
        "bullet_shape": "circle",
        "bullet_color": ORANGE,
    },
}
```

### Bullet Visual

`Bullet` constructor accepts `radius`, `shape`, `color`. `draw()` branches:
- `"circle"` — `pygame.draw.circle` (existing)
- `"rect"` — 4-point polygon rotated to velocity direction (~4×10px)

### Shotgun Firing

`player.shoot()` spawns `pellets` bullets, each offset by an angle sampled uniformly within `±spread/2` degrees of `self.facing`. Each pellet is an independent `Bullet` instance.

---

## 3. Reward System

### Two Tiers

| Trigger | Pool | Feel |
|---------|------|------|
| XP level-up (existing) | Stat upgrades | Small, frequent |
| Room complete (new) | Weapons + augments | Big, infrequent |

Level-up screen unchanged. Room reward screen: same 3-card layout and 1/2/3 + click input, different card content.

### Room Reward Pool

Cards drawn from weighted pool:
- Weapon cards — only shown if player doesn't already have that weapon
- Augment cards — always available

Once all weapons are acquired, pool is augments only.

### Augments (`settings.py`)

```python
AUGMENTS = {
    "laser_pointer": {
        "name": "Laser Pointer",
        "desc": "Projects a laser sight. Visual only.",
        "stat_changes": {},          # no mechanical effect
        "visual": "laser",
    },
    "fast_loader": {
        "name": "Fast Loader",
        "desc": "-30% reload time, -15% damage.",
        "stat_changes": {"reload": 0.70, "damage": 0.85},  # multipliers
    },
    "hollow_point": {
        "name": "Hollow Point",
        "desc": "+40% damage, +15° spread.",
        "stat_changes": {"damage": 1.40, "spread": 15},    # spread is additive degrees
    },
    "drum_mag": {
        "name": "Drum Mag",
        "desc": "×2 mag size, +50% reload time.",
        "stat_changes": {"mag": 2.0, "reload": 1.50},      # multipliers
    },
}
```

`Player.equip_augment(augment_def)` appends to `self.augments` (max 2). Effective stats computed on read: `player.effective_damage()`, `player.effective_reload()`, etc. — multiply base weapon stat by all augment multipliers.

**Augments are weapon-bound.** `Player.equip(weapon_def)` clears `self.augments`. Swapping a kitted weapon means losing augments — intentional tension.

### Laser Pointer Rendering

`player.draw()` checks if `"laser_pointer"` in augments. If so, draws a thin red line from player position toward mouse cursor, fading to alpha=0 at 300px or arena edge.

### HUD Augment Display

Small text labels below the ammo counter showing active augment names.

---

## 4. Boss

Boss room spawns two elite enemies simultaneously. No wave spawning during boss fight.

| Entity | HP mult | Size | Behaviour change |
|--------|---------|------|-----------------|
| Mutant Boss | ×5 | 40×40 red rect | 1.5× speed |
| Bandit Boss | ×5 | 48×48 blue rect | 2× fire rate |

Both must die to complete the boss room and trigger win state.

Implemented as `hp_mult` and `size` kwargs on existing `Mutant`/`Bandit` constructors — no new classes needed.

---

## 5. Files Changed

| File | Change |
|------|--------|
| `settings.py` | Add `ROOM_SEQUENCE`, `WEAPONS`, `AUGMENTS`; remove `WIN_TIME` |
| `systems/run_manager.py` | **New** — run state machine |
| `entities/player.py` | Weapon as data; `equip()`, `equip_augment()`, effective stat methods |
| `entities/projectile.py` | `Bullet` accepts `radius`, `shape`, `color` |
| `systems/wave_manager.py` | Accept `start_tier` offset param |
| `ui/hud.py` | `draw_room_reward()` (new); `draw_win_screen` update; augment HUD |
| `main.py` | Replace flat state flags with `run_manager.state`; wire boss spawn |

---

## 6. Out of Scope (Future Milestones)

- Map screen / branching paths
- SMG and additional weapons
- Unique boss with special attacks
- More augment types
- Persistent meta-progression / character unlocks
- Protect / extraction objective types
- Art assets / tilemap
