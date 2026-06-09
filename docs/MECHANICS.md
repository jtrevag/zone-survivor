# Mechanics Reference

## Reload System
The core skill mechanic of the game. Rules:

- Player has a current ammo count and a mag size
- Firing costs 1 ammo; at 0 ammo the player cannot fire
- Pressing `R` at any ammo count initiates a reload (even partial mag)
- Reload takes `reload_time` seconds — no firing during this window
- Reload completes instantly at end of timer (no partial reload)
- HUD shows: `[current] / [mag_size]` and a progress bar during reload
- Empty-click (firing with 0 ammo) plays a dry-fire sound and flashes the ammo counter

**Design intent:** The player must decide whether to reload proactively (safe, wastes ammo) or reactively (risky, may be caught in reload). Mutants punish reactive reloaders hard.

---

## Movement
- WASD, 8-directional
- Player rotates to face mouse cursor continuously
- Speed is flat (no acceleration/deceleration in v1)
- Arena has hard boundaries — player cannot leave screen

---

## Combat

### Player Firing
- Left click fires one round if ammo > 0 and not reloading
- Bullet travels in direction of mouse cursor at time of click
- Bullet despawns on hit or on leaving arena bounds
- Short cooldown between shots (~0.4s) to reinforce bolt-action feel

### Enemy — Bandit
- Aggro range: full screen (always aware of player)
- Preferred range: ~250px from player
- Fires a projectile every 2.5 seconds when within preferred range
- Bandit projectiles travel slower than player bullets
- HP: 80 (2 shots at base damage)

### Enemy — Mutant
- Aggro range: full screen
- Moves directly toward player at all times
- No ranged attack
- Deals 15 damage on contact, once per 0.5s
- HP: 35 (1 shot at base damage)

---

## XP & Leveling
- Enemies drop XP orbs on death
  - Bandit: 10 XP
  - Mutant: 5 XP
- Orbs persist on ground for 10 seconds then despawn
- Player collects orbs by walking over them
- XP required per level: `50 * level` (level 1→2 = 50 XP, 2→3 = 100 XP, etc.)
- On level-up: game pauses, upgrade screen shown, 3 random upgrades offered
- Player picks one, game resumes

---

## Wave Scaling
Waves are time-based. The `wave_manager` ticks every 60 seconds.

| Minute | Spawn Rate | Mutant % | Bandit HP Mult |
|--------|-----------|----------|----------------|
| 0-1    | 1 enemy/3s | 20%     | 1.0x           |
| 2-3    | 1 enemy/2s | 30%     | 1.0x           |
| 4-5    | 1 enemy/1.5s | 40%  | 1.2x           |
| 6-9    | 1 enemy/1s | 50%     | 1.5x           |
| 10+    | 1 enemy/0.7s | 60%   | 2.0x           |

Enemies spawn at random points along arena edges, outside player view when possible.

---

## Collision
- Player ↔ Bandit projectile: player takes damage
- Player ↔ Mutant: player takes damage (contact)
- Player bullet ↔ Enemy: enemy takes damage, bullet despawns
- Player bullet ↔ Player bullet: no interaction
- Enemies ↔ Enemies: no collision (overlap allowed in v1)

---

## Player Death & Restart
- Player dies when HP reaches 0
- Game freezes on death (enemies stop, spawner stops)
- Game-over overlay displayed: "GAME OVER" + "Press R to restart"
- R key from game-over state resets all game objects (player, enemies, bullets, spawner) to initial state
- ESC still quits from game-over state

---

## Spawning (Milestone 3)
- Mutants only (Bandits added in M4)
- Spawn rate: 1 Mutant every 3 seconds
- Spawn position: random point along arena edge (top/bottom/left/right wall)
