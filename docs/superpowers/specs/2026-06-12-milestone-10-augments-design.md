# M10 — Augments & Room Rewards: Design Spec

**Date:** 2026-06-12
**Milestone:** 10
**Branch:** feat/milestone-10-augments (to be created)

---

## Overview

Augments are weapon-specific power-ups awarded at room-clear reward screens. They are stronger than level-up upgrades but clear when you swap weapons — trade breadth (upgrades, always on) for depth (augments, weapon-locked).

**Stat stack:**
```
weapon base stat
  × upgrade multipliers  (baked in by equip() replay — persist across swaps)
  × augment multipliers  (computed at use-time via effective_*() — cleared on swap)
= final value
```

---

## Data Layer (`settings.py`)

### AUGMENTS dict

Five augments. Each is a dict with `id`, `name`, `desc`, plus optional multiplier/behaviour keys read by `effective_*()` methods.

| id | name | effect keys | notes |
|---|---|---|---|
| `laser_pointer` | Laser Sight | _(none)_ | Visual only — presence triggers rendering |
| `fast_loader` | Fast Loader | `reload_time_mult: 0.75` | −25% reload (stronger than upgrade's 0.80) |
| `hollow_point` | Hollow Point | `pierce_count: 1, pierce_damage_mult: 0.5` | Pistol-only. Bullet pierces one enemy at 50% dmg |
| `drum_mag` | Drum Mag | `mag_size_mult: 2.0` | ×2 mag size on next reload |
| `more_pellets` | More Pellets | `pellet_bonus: 2` | Shotgun-only. 4 → 6 pellets, same 25° spread |

### Weapon augment pools

Each weapon def gains an `augments` list of compatible augment IDs:

```python
'pistol':  { ..., 'augments': ['laser_pointer', 'fast_loader', 'hollow_point', 'drum_mag'] }
'shotgun': { ..., 'augments': ['laser_pointer', 'fast_loader', 'more_pellets', 'drum_mag'] }
```

Reward card generation draws 2 augments from `player.weapon['augments']`.

---

## Player (`entities/player.py`)

### `equip_augment(augment_def)`

Appends augment to `self.augments` (max 2). Silently no-ops if full.  
`equip()` already does `self.augments = []` on weapon swap — no change needed.

### Effective stat methods

Non-mutating. Read `self.augments` at call time. Return base stat × product of relevant multipliers.

```python
def effective_damage(self):       # int(self.damage × damage_mult augments)
def effective_reload_time(self):  # self.reload_time × reload_time_mult augments
def effective_mag_size(self):     # int(self.mag_size × mag_size_mult augments)
def effective_pellets(self):      # self.weapon['pellets'] + sum pellet_bonus augments
def effective_pierce(self):       # returns (pierce_count, pierce_damage_mult) from augments
```

### `try_fire()` changes

- Bullet damage → `self.effective_damage()`
- Pellet count → `self.effective_pellets()`
- Pierce params → `self.effective_pierce()` passed to `Bullet`

### Reload changes

- Progress denominator → `self.effective_reload_time()`
- On reload complete → `self.ammo = self.effective_mag_size()` (drum_mag takes effect at reload)

### `draw(surface, enemies=None)`

When `laser_pointer` augment active:
- Cast ray from `player.pos` toward cursor, max 300 px
- Find nearest enemy whose `rect.clipline(start, end)` returns a hit
- Clip line to that intersection (or 300 px if no enemy in path)
- Draw outer dim red line (width 3, low alpha) + inner bright red line (width 1), both fade to α=0 at endpoint

---

## Bullet (`entities/projectile.py`)

### Constructor changes

```python
Bullet(..., pierce_count=0, pierce_damage_mult=0.5)
```

Stores `self.pierce_count` and `self.pierce_damage_mult`.

### `on_hit(enemy)` method

Called by main loop on bullet↔enemy collision. Returns `True` if bullet should die, `False` if it pierces.

```
if pierce_count > 0:
    deal self.damage to enemy
    self.damage = int(self.damage * self.pierce_damage_mult)
    self.pierce_count -= 1
    return False  # bullet continues
else:
    deal self.damage to enemy
    return True   # bullet dies
```

---

## Collision (`main.py`)

Replace `groupcollide(bullets, enemies, True, True)` with a manual loop:

```
for bullet in list(bullets):  # copy — safe to kill during iteration
    for enemy in pygame.sprite.spritecollide(bullet, enemies, False):
        if bullet.on_hit(enemy):
            bullet.kill()
            break
        # pierced — continue to next enemy this frame
```

---

## Room Reward Screen

### Card generation (on REWARD transition)

- Card 1: the OTHER weapon (not currently equipped)
- Cards 2–3: 2 augments sampled without replacement from `player.weapon['augments']`, excluding augments already in `player.augments`; pool of 4 with max 2 equipped always leaves ≥ 2 to draw
- Cards generated once on transition, stored in main loop local var

### `HUD.draw_reward(surface, cards, mouse_pos)`

Reuses `_card_rects` and card rendering from `draw_level_up()`. Replaces `draw_room_clear()` entirely — "ROOM CLEAR" becomes the overlay title.

**Weapon card** (always card 1):
- Header: `SWAP → [WeaponName]`
- Body: key stats (damage, mag, reload)
- Footer dim red: `Augments reset`

**Augment card**:
- Header: augment name
- Body: desc
- Footer dim grey: `Attaches to [CurrentWeaponName]`
- If `len(player.augments) >= 2`: show `FULL` label, card not selectable

### Input handling (main.py REWARD state)

- `1`/`2`/`3` keys or click on card → apply selection → `run_manager.advance()`
- Weapon selection: `player.equip(WEAPONS[weapon_id])`
- Augment selection: `player.equip_augment(AUGMENTS[augment_id])` (no-op if full)

---

## Pause Screen

### Toggle

ESC during ENCOUNTER state toggles `paused` bool in main.py. When `paused`, skip `all_sprites.update()`, collision, and `run_manager.update()`.

### `HUD.draw_pause(surface, player)`

Semi-transparent overlay, two columns:

- **Left — Upgrades:** heading + list of upgrade names from `player._upgrade_history` (deduplicated with counts, e.g. "Faster Reload ×2")
- **Right — Weapon:** current weapon name, augments as indented bullet list

Footer: `ESC to resume`

---

## HUD In-Game Augment Display

Extend `HUD.draw()` bottom-left block. Below weapon name, list active augments in small grey text:

```
Shotgun          ← existing weapon label
• More Pellets   ← new, only shown if augments active
• Drum Mag
```

No change needed if `player.augments` is empty.

---

## Files Changed

| File | Change |
|---|---|
| `settings.py` | Add `AUGMENTS` dict; add `augments` list to each weapon def |
| `entities/player.py` | `equip_augment()`, `effective_*()` methods, `try_fire()` + reload updates, `draw()` laser pointer |
| `entities/projectile.py` | `Bullet`: `pierce_count`/`pierce_damage_mult` params, `on_hit()` method |
| `main.py` | Manual bullet collision loop, REWARD card generation + input, `paused` flag + ESC toggle |
| `ui/hud.py` | `draw_reward()`, `draw_pause()`, augment list in `draw()` |

---

## Out of Scope (M10)

- Boss room (M11)
- Additional weapons beyond pistol/shotgun
- Augment synergies or stacking beyond 2 slots
