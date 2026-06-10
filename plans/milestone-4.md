# Milestone 4 — Second Enemy (Bandit)

## Context
Milestone 3 shipped a single melee enemy (Mutant). Milestone 4 adds a ranged enemy (Bandit) that closes to a preferred distance and fires projectiles at the player. Both types must spawn simultaneously. This introduces the game's first "incoming fire" mechanic, which pairs with the reload system as the core tension of the loop.

---

## Scope (from ROADMAP.md)
- Bandits spawn and pathfind toward player
- Bandits stop at preferred range and fire
- Bandit projectiles travel and damage player
- Both enemy types active simultaneously

---

## Stats (from ENTITIES.md / MECHANICS.md)
| Property | Value |
|---|---|
| Size | 24×24 blue rect |
| move_speed | 60 px/s |
| max_hp | 80 (2 player shots) |
| preferred_range | 250 px |
| resume_chase_range | 300 px (hysteresis — resume chase if player backs away) |
| fire_interval | 2.5 s |
| projectile_speed | 180 px/s |
| projectile_damage | 12 |
| projectile placeholder | orange circle r=3 |

---

## Implementation Plan

### 1. `settings.py`
Add Bandit and BanditProjectile constants:
```python
BANDIT_COLOR = (60, 100, 220)
BANDIT_SIZE = 24
BANDIT_SPEED = 60
BANDIT_MAX_HP = 80
BANDIT_PREFERRED_RANGE = 250
BANDIT_RESUME_CHASE_RANGE = 300
BANDIT_FIRE_INTERVAL = 2.5
BANDIT_PROJECTILE_SPEED = 180
BANDIT_PROJECTILE_RADIUS = 3
BANDIT_PROJECTILE_COLOR = (255, 140, 0)
BANDIT_PROJECTILE_DAMAGE = 12
```

### 2. `entities/projectile.py`
Add `BanditProjectile` class alongside `Bullet`. Same despawn-at-edge logic, different speed/radius/color/damage. `update(dt, player=None)` signature preserved.

### 3. `entities/enemy.py`
Add `Bandit` class. Constructor takes `(pos, all_sprites, bandit_projectiles)` and stores group refs so it can fire directly into them.

Behavior in `update(dt, player=None)`:
1. Compute distance to player.
2. Hysteresis via `_chasing` bool (starts `True`):
   - Chasing and dist ≤ PREFERRED_RANGE → stop chasing
   - Not chasing and dist > RESUME_CHASE_RANGE → resume chasing
3. If chasing: move toward player (same vector math as Mutant).
4. If not chasing: tick `_fire_timer`; on expiry reset timer and spawn a `BanditProjectile` aimed at player's current pos, added to both groups.

`take_damage` and `draw` follow the same pattern as `Mutant`.

### 4. `systems/spawner.py`
- `update()` gains `bandit_projectiles` param
- Each spawn randomly picks `Mutant` or `Bandit` (50/50; wave scaling is M6)
- Passes `(pos, all_sprites, bandit_projectiles)` to `Bandit`, `(pos,)` to `Mutant`

### 5. `main.py`
- `new_game()` creates `bandit_projectiles = pygame.sprite.Group()` and returns it
- Both call sites (`new_game()` at start and on restart) unpack the new value
- `spawner.update()` receives `bandit_projectiles`
- After `all_sprites.update()`, add player ↔ bandit projectile collision:
  ```python
  for proj in pygame.sprite.spritecollide(player, bandit_projectiles, True):
      player.take_damage(proj.damage)
  ```
  (Bandit projectiles add themselves to `all_sprites` on creation for update/draw; `bandit_projectiles` is a separate group used only for this collision query.)

### 6. `docs/CHANGELOG.md`
Add M4 entry.

---

## Files Changed
| File | Change |
|---|---|
| `settings.py` | +11 Bandit/BanditProjectile constants |
| `entities/projectile.py` | +`BanditProjectile` class |
| `entities/enemy.py` | +`Bandit` class |
| `systems/spawner.py` | spawn both types; pass groups to Bandit |
| `main.py` | new group, collision check, updated `new_game()` |
| `docs/CHANGELOG.md` | M4 entry |

---

## Verification
1. `source .venv/bin/activate && python3 main.py`
2. Blue rects (Bandits) and red rects (Mutants) both spawn from arena edges
3. Bandits close to ~250 px, stop, fire orange circles toward player
4. Orange projectiles damage player HP (visible on HUD)
5. Bandits resume chasing if player backs away past ~300 px
6. Player bullets kill Bandits in 2 hits
7. Restart from game-over clears all enemies and projectiles cleanly
