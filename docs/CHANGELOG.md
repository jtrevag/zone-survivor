# Changelog

Track what changed, when, and why. Format: `## vX.X — YYYY-MM-DD`

---

## v0.5 — 2026-06-09
- Milestone 4: second enemy (Bandit)
- `entities/enemy.py`: `Bandit` class — blue 24×24 rect, 60 px/s, 80 HP (2 player shots); closes to 250 px preferred range then stops and fires; resumes chase if player backs past 300 px (hysteresis)
- `entities/projectile.py`: `BanditProjectile` class — orange circle r=3, 180 px/s, 12 damage; self-registers to `all_sprites` and `bandit_projectiles` on spawn
- `systems/spawner.py`: now spawns Mutant or Bandit at 50/50 odds each tick; receives `bandit_projectiles` group to pass to Bandit constructor
- `main.py`: `new_game()` now returns `bandit_projectiles` group; player↔bandit projectile collision kills projectile and calls `player.take_damage(proj.damage)` each frame
- `settings.py`: +11 Bandit/BanditProjectile constants
- Docs: `ROADMAP.md` M4 checked off

---

## v0.4 — 2026-06-09
- Milestone 3: first enemy (Mutant)
- `entities/enemy.py`: Mutant class — red 20×20 rect, 140 px/s, 35 HP, chases player directly, deals 15 contact damage per 0.5s
- `systems/spawner.py`: timer-based spawner, 1 Mutant every 3s at a random arena edge
- `entities/player.py`: added `max_hp`, `hp`, `dead`, `take_damage()` — player dies at 0 HP
- `entities/projectile.py`: `Bullet` now carries `damage = PLAYER_DAMAGE (40)` — one-shots mutants
- `ui/hud.py`: HP bar at top-left (label + red fill bar); game-over overlay with "Press R to restart"
- `main.py`: `new_game()` reset function; separate `enemies`/`bullets` groups; `groupcollide` for bullet↔enemy; R from game-over triggers full reset
- `settings.py`: added `PLAYER_MAX_HP`, `PLAYER_DAMAGE`, all mutant constants, `SPAWN_INTERVAL`, HP-bar HUD colors, `HUD_FONT_SIZE_LARGE`
- Docs: `MECHANICS.md` updated with death/restart and M3 spawn rules; `ROADMAP.md` M2 and M3 checked off

---

## v0.3 — 2026-06-09
- Python 3.12 venv added (`.venv/`) — workaround for pygame 2.6.1 circular import bug between `pygame.font` and `pygame.sysfont` that Python 3.14 rejects; upstream fix tracked at pygame/pygame#4607
- `.venv/` added to `.gitignore`; `CLAUDE.md` updated with venv activation step
- Milestone 2: combat basics
- Left-click fires a yellow bullet toward mouse cursor (500 px/s, despawns at arena edge)
- Ammo counter (5-round mag); empty-click does nothing
- R key starts 2s reload; cannot fire during reload; reload completes to full mag
- 0.4s shot cooldown enforces bolt-action pacing
- HUD: ammo counter (bottom-left) + reload progress bar
- New files: `entities/projectile.py`, `ui/hud.py`
- `settings.py` extended with bullet, reload, shot cooldown, and HUD constants

---

## v0.2 — 2026-06-09
- Milestone 1 complete: moving player
- Pygame window 1280×720 @ 60fps with ESC to quit
- WASD movement with normalized diagonals (flat speed in all directions)
- Arena bounds clamp on circle edge, not center
- Player faces mouse cursor with visible direction indicator line
- All constants in `settings.py`; `main.py` is loop-only
- Code review fixes:
  - `dt` capped at 50ms to prevent first-frame teleport on slow hardware
  - `all_sprites.update(dt, player)` — future enemies receive player ref via group update
  - Entity draw loop (`for entity in all_sprites`) replaces direct `player.draw()` — scales to M2+ entities
  - `self.facing` (normalized Vector2) replaces angle + cos/sin polar round-trip; M2 uses `facing` for bullet velocity
  - Event pump ordering documented; `player=None` param on `Player.update` for group broadcast compat
  - Sub-pixel fix: indicator tip based on `rect.center`, not raw float `pos`
  - Removed unused `BLACK` constant from `settings.py`

---

## v0.1 — 2026-06-09
- Initial design document drafted
- Core fantasy defined: methodical survival, reload timing as skill expression
- Enemy types defined: Bandit (ranged, slow) and Mutant (melee, fast)
- Upgrade system outlined
- Wave scaling table established
- Build roadmap created (7 milestones)
