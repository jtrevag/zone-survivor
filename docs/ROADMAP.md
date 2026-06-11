# Build Roadmap

Milestones are ordered by dependency. Each milestone should be playable/testable before moving on. Don't add content until the loop it belongs to is complete.

---

## Milestone 1 — Moving Player ✓
- [x] Pygame window opens at 1280x720, 60fps
- [x] Player (white circle) renders in center
- [x] WASD movement with arena bounds
- [x] Player rotates to face mouse cursor
- [x] `settings.py` holds all constants

---

## Milestone 2 — Combat Basics ✓
- [x] Left click fires a bullet toward mouse cursor
- [x] Bullet travels and despawns at arena edge
- [x] Ammo counter decrements on fire
- [x] Empty-click does nothing (no fire at 0 ammo)
- [x] R key initiates reload with timer
- [x] Cannot fire during reload
- [x] HUD: ammo counter + reload progress bar

---

## Milestone 3 — First Enemy (Mutant) ✓
- [x] Mutants spawn at arena edges
- [x] Mutants chase player directly
- [x] Player bullets hit and kill mutants
- [x] Mutants deal contact damage to player
- [x] Player HP displayed on HUD
- [x] Player death state (game over screen, restart)

---

## Milestone 4 — Second Enemy (Bandit) ✓
- [x] Bandits spawn and pathfind toward player
- [x] Bandits stop at preferred range and fire
- [x] Bandit projectiles travel and damage player
- [x] Both enemy types active simultaneously

---

## Milestone 5 — XP & Leveling
- [x] Enemies drop XP orbs on death
- [x] Player collects orbs on contact
- [x] XP bar on HUD
- [x] Level-up screen pauses game
- [x] 3 random upgrades offered, player picks one
- [x] Upgrades apply correctly to player stats

---

## Milestone 6 — Wave Scaling ✓
- [x] Wave manager ticks on 60s intervals
- [x] Spawn rate increases per wave table
- [x] Mutant ratio increases over time
- [x] Bandit HP scales after minute 5

---

## Milestone 7 — Win Condition & Polish Pass ✓
- [x] 20-minute survival timer on HUD
- [x] Win screen on timer completion
- [x] Death screen shows time survived
- [x] Restart works cleanly from both screens
- [x] Basic sound effects (gunshot, reload, hit, death)
- [x] Screen flash on player hit

---

## Milestone 8 — Run Structure
- [ ] `RunManager` (`systems/run_manager.py`) — state machine: `ENCOUNTER → ROOM_COMPLETE → REWARD → ... → WIN`
- [ ] Room types: `survive` (elapsed ≥ duration), `kill_count` (kills ≥ target), `boss` (all bosses dead)
- [ ] 3-room + boss sequence in `settings.py` (`ROOM_SEQUENCE`); difficulty maps to `WaveManager` time offset
- [ ] `WaveManager` accepts `time_offset` param — initialises `self.elapsed = time_offset`
- [ ] Room reset between rooms — clear enemies, projectiles, XP orbs; player HP and weapon carry over
- [ ] Replace `game_over`/`game_won` flags in `main.py` with `run_manager.state`

---

## Milestone 9 — Weapons
- [ ] Weapons as data — move weapon stats out of `Player` into `WEAPONS` dict (`settings.py`)
- [ ] `Player.equip(weapon_def)` — sets `self.weapon`, resets ammo, clears augments
- [ ] Shotgun weapon definition — 2-shot mag, 4 pellets, 25° spread cone
- [ ] `Bullet` accepts `radius`, `shape`, `color`; `draw()` handles `"circle"` and `"rect"` (rotated polygon)

---

## Milestone 10 — Augments & Room Rewards
- [ ] `AUGMENTS` dict in `settings.py` — laser_pointer, fast_loader, hollow_point, drum_mag
- [ ] `Player.equip_augment(augment_def)` — appends to `self.augments` (max 2); augments clear on weapon swap
- [ ] Effective stat methods (`effective_damage()`, `effective_reload()`, etc.) — multiply base by augment multipliers
- [ ] Room reward screen — 3-card layout (weapon + augment cards); reuses level-up input (1/2/3 + click)
- [ ] Laser pointer rendering — thin red line from player toward cursor, fades to α=0 at 300px
- [ ] HUD augment display — active augment names below ammo counter

---

## Milestone 11 — Boss Room
- [ ] Mutant Boss (×5 HP, 40×40 red rect, 1.5× speed) and Bandit Boss (×5 HP, 48×48 blue rect, 2× fire rate) via `hp_mult`/`size` kwargs on existing constructors
- [ ] Boss room spawns both simultaneously; no wave spawning during boss fight
- [ ] Win state triggers after both bosses dead

---

## Post-v1 (Backlog)
- [x] Web deploy — playable HTML5 prototype on itch.io (Pygbag/WASM)
- Map screen / branching paths (Slay the Spire style)
- SMG and additional weapons beyond shotgun
- Unique boss with special attacks
- More augment types
- Cover/obstacles in arena
- Persistent meta-progression / character unlocks
- Tilemap / real art assets
- Controller support
