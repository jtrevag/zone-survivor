# Milestone 5 Implementation Plan — XP & Leveling

## Goal
Add XP orbs, player leveling, and an upgrade selection screen. When an enemy dies
it drops an orb; the player collects orbs by walking over them; at each level-up
the game pauses and the player picks one of three random upgrades.

---

## Checklist (from ROADMAP.md)
- [ ] Enemies drop XP orbs on death
- [ ] Player collects orbs on contact
- [ ] XP bar on HUD
- [ ] Level-up screen pauses game
- [ ] 3 random upgrades offered, player picks one
- [ ] Upgrades apply correctly to player stats

---

## Files to Change

| File | Type | Summary |
|------|------|---------|
| `settings.py` | Modify | Add orb constants, XP constants, upgrade multipliers, UPGRADES list |
| `entities/xp_orb.py` | **New** | XPOrb sprite — lifetime, proximity pickup, green circle draw |
| `entities/enemy.py` | Modify | Add `xp_value` attribute to Mutant and Bandit |
| `entities/player.py` | Modify | Mutable stats, XP tracking, `collect_xp()`, `apply_upgrade()` |
| `ui/hud.py` | Modify | XP bar in `draw()`, new `draw_level_up()` method |
| `main.py` | Modify | `xp_orbs` group, orb spawning on kill, level-up pause state |

`systems/xp_system.py` (listed in CLAUDE.md structure) is not needed — XP state
lives on the player and the logic is too simple to warrant a separate system.

---

## Task 1 — `settings.py`: New Constants

```python
# XP orb
XP_ORB_RADIUS = 5
XP_ORB_COLOR = (50, 200, 50)
XP_ORB_LIFETIME = 10.0          # seconds before despawn
XP_ORB_PICKUP_RADIUS = 20       # px, player-center to orb-center
XP_ORB_PICKUP_RADIUS_SQ = XP_ORB_PICKUP_RADIUS ** 2

# Enemy XP values
MUTANT_XP_VALUE = 5
BANDIT_XP_VALUE = 10

# XP / leveling
XP_PER_LEVEL_BASE = 50          # xp_to_next = 50 * current_level

# Upgrade multipliers
UPGRADE_MAG_BONUS       = 2
UPGRADE_RELOAD_MULT     = 0.80  # -20% reload time
UPGRADE_DAMAGE_MULT     = 1.25  # +25% damage
UPGRADE_SPEED_MULT      = 1.10  # +10% speed
UPGRADE_HP_BONUS        = 20
UPGRADE_FIRE_RATE_MULT  = 0.85  # -15% shot cooldown

# Upgrade definitions — consumed by HUD and main loop
UPGRADES = [
    {'id': 'mag',       'name': 'Larger Mag',   'desc': '+2 rounds'},
    {'id': 'reload',    'name': 'Faster Reload', 'desc': '-20% reload time'},
    {'id': 'damage',    'name': 'More Damage',   'desc': '+25% damage'},
    {'id': 'speed',     'name': 'Move Speed',    'desc': '+10% speed'},
    {'id': 'hp',        'name': 'Max HP',        'desc': '+20 HP'},
    {'id': 'fire_rate', 'name': 'Fire Rate',     'desc': '-15% shot cooldown'},
]

# HUD additions
HUD_COLOR_XP_BG   = (30, 30, 80)
HUD_COLOR_XP_FILL = (80, 130, 255)
```

---

## Task 2 — `entities/xp_orb.py`: New File

```python
class XPOrb(pygame.sprite.Sprite):
    def __init__(self, pos, value):
        # pos: Vector2 or tuple; value: int XP
        # self._lifetime = XP_ORB_LIFETIME

    def update(self, dt, player=None):
        # 1. self._lifetime -= dt; kill() if <= 0
        # 2. if player and not player.dead:
        #        if (player.pos - self.pos).length_squared() <= XP_ORB_PICKUP_RADIUS_SQ:
        #            player.collect_xp(self.value)
        #            self.kill()

    def draw(self, surface):
        # pygame.draw.circle(surface, XP_ORB_COLOR, center, XP_ORB_RADIUS)
```

The orb calls `player.collect_xp()` directly on contact — same pattern mutants use
for `player.take_damage()`. No return value needed; level-up detection happens
via `player.pending_level_up` polled in the main loop.

---

## Task 3 — `entities/enemy.py`: Add `xp_value`

In `Mutant.__init__`:
```python
self.xp_value = MUTANT_XP_VALUE
```

In `Bandit.__init__`:
```python
self.xp_value = BANDIT_XP_VALUE
```

No other changes to enemy code.

---

## Task 4 — `entities/player.py`: Mutable Stats + XP

### `__init__` additions

Replace hard-coded constant references with mutable instance variables so
upgrades can modify them at runtime:

```python
self.damage            = PLAYER_DAMAGE
self.move_speed        = PLAYER_SPEED
self.mag_size          = PLAYER_MAG_SIZE
self.reload_time       = PLAYER_RELOAD_TIME
self.shot_cooldown_base = PLAYER_SHOT_COOLDOWN

self.xp               = 0
self.level            = 1
self.xp_to_next       = XP_PER_LEVEL_BASE   # 50 * level
self.pending_level_up = False
```

### `update()` changes

Swap every constant reference for the corresponding instance variable:

| Old | New |
|-----|-----|
| `PLAYER_SPEED` | `self.move_speed` |
| `PLAYER_RELOAD_TIME` | `self.reload_time` |
| `PLAYER_SHOT_COOLDOWN` | `self.shot_cooldown_base` |
| `PLAYER_MAG_SIZE` (reload completion) | `self.mag_size` |

### New: `collect_xp(amount)`

```python
def collect_xp(self, amount):
    self.xp += amount
    if self.xp >= self.xp_to_next:
        self.xp -= self.xp_to_next
        self.level += 1
        self.xp_to_next = XP_PER_LEVEL_BASE * self.level
        self.pending_level_up = True
```

### New: `apply_upgrade(upgrade_id)`

```python
def apply_upgrade(self, upgrade_id):
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
```

---

## Task 5 — `ui/hud.py`: XP Bar + Level-Up Screen

### XP bar in `draw()`

Add an XP bar below the HP section (or anchored above the reload bar). Bar width
matches `HUD_BAR_WIDTH`; ratio = `player.xp / player.xp_to_next`.

Also fix the ammo label: currently hardcodes `PLAYER_MAG_SIZE`; change to
`player.mag_size` so the upgraded mag size renders correctly.

### New: `draw_level_up(surface, upgrades, mouse_pos)`

```
Layout (full-screen overlay):
  - Semi-transparent dark fill (0,0,0,180)
  - "LEVEL UP" centred, large font
  - Three cards side-by-side, each showing:
      - Upgrade name (large)
      - Description (small)
      - Key hint: "Press 1 / 2 / 3"
  - Card under mouse_pos gets a highlight border

Returns: index (0-2) of the hovered card, so main.py can map clicks to choices.
         Returns -1 when no card is hovered.
```

Cards are pre-computed rects so hit-testing in main.py is straightforward.
Expose them via `self.upgrade_card_rects` after the first `draw_level_up` call,
or compute + return them each frame (simpler, acceptable at 60fps pause).

---

## Task 6 — `main.py`: Wire Everything

### `new_game()` additions

```python
xp_orbs = pygame.sprite.Group()
# add to return tuple
```

### Orb spawning on kill

After `enemy.take_damage(bullet.damage)`, if the enemy's hp is now 0, spawn an orb:

```python
hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
for bullet, hit_enemies in hits.items():
    for enemy in hit_enemies:
        enemy.take_damage(bullet.damage)
        if enemy.hp <= 0:
            orb = XPOrb(enemy.pos, enemy.xp_value)
            all_sprites.add(orb)
            xp_orbs.add(orb)
```

(`take_damage` already calls `enemy.kill()` when hp hits 0, so the enemy is
removed from groups; `enemy.hp` is still readable after the call.)

### Level-up pause state

```python
level_up = False
pending_upgrades = []
```

In the update block:

```python
if not game_over and not level_up:
    all_sprites.update(dt, player)
    spawner.update(dt, all_sprites, enemies, bandit_projectiles)
    # ... collision handling ...
    if player.pending_level_up:
        player.pending_level_up = False
        level_up = True
        pending_upgrades = random.sample(UPGRADES, 3)
```

### Event handling for upgrade selection

```python
elif level_up:
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_1:   player.apply_upgrade(pending_upgrades[0]['id']); level_up = False
        elif event.key == pygame.K_2: player.apply_upgrade(pending_upgrades[1]['id']); level_up = False
        elif event.key == pygame.K_3: player.apply_upgrade(pending_upgrades[2]['id']); level_up = False
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        idx = hud.hovered_upgrade(event.pos, pending_upgrades)
        if idx >= 0:
            player.apply_upgrade(pending_upgrades[idx]['id'])
            level_up = False
```

### Draw call

```python
if level_up:
    hud.draw_level_up(screen, pending_upgrades, pygame.mouse.get_pos())
```

---

## Upgrade Table (from GDD.md)

| ID | Name | Effect |
|----|------|--------|
| `mag` | Larger Mag | +2 rounds |
| `reload` | Faster Reload | -20% reload time |
| `damage` | More Damage | +25% damage |
| `speed` | Move Speed | +10% speed |
| `hp` | Max HP | +20 HP |
| `fire_rate` | Fire Rate | -15% shot cooldown |

---

## SDLC Sequence (per CLAUDE.md)

1. Implement all tasks above in order
2. Play-test (human checkpoint 1)
3. `/simplify`
4. `/code-review`
5. Play-test (human checkpoint 2)
6. Create PR
