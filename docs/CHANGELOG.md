# Changelog

Track what changed, when, and why. Format: `## vX.X — YYYY-MM-DD`

---

## v0.9 — 2026-06-11
- Web deploy: playable HTML5 prototype on itch.io via Pygbag (WASM)
- `main.py`: refactored `main()` to `async def`, added `await asyncio.sleep(0)` per frame, changed entry point to `asyncio.run(main())` — required for Pygbag/browser event loop
- `requirements.txt`: added `pygbag>=0.9.0`
- `pygbag.ini`: added exclude list for dev dirs (`.venv`, `.agents`, `.claude`, `tests`, `docs`, `build`, cache dirs) — paths must use leading `/` to match pygbag's gathered path format
- `.gitignore`: added `build/` and `zone-survivor-web.zip`

## v0.8 — 2026-06-10
- Milestone 7: win condition & polish
- `systems/wave_manager.py`: added `is_complete` property — returns `True` when elapsed >= `WIN_TIME` (1200s)
- `entities/player.py`: added `hit_flash_timer` (counts down from `HIT_FLASH_DURATION` on damage), `just_hit` bool (sound trigger, cleared by main loop), `reload_complete` bool (sound trigger, set when reload finishes, cleared by main loop)
- `systems/sound_manager.py`: new `SoundManager` — generates 4 synthetic sounds at init via sine wave / frequency-sweep PCM (no audio files); exposes `play_gunshot()`, `play_reload()`, `play_hit()`, `play_death()`
- `ui/hud.py`: replaced static `_build_game_over_surf` with lazy `_build_end_screen(title, color, elapsed_sec)` shared by both screens; `draw_game_over(surface, elapsed)` now shows time survived; new `draw_win_screen(surface, elapsed)` — "YOU SURVIVED" in gold with time survived
- `main.py`: `game_won` state added; `pygame.mixer.pre_init()` before `pygame.init()`; `SoundManager` instantiated once; pre-allocated `_flash_surf` for hit flash; R key restarts from both game-over and win screens; gunshot/hit/reload/death sounds wired to events; hit flash overlay scaled by remaining `hit_flash_timer`; update gated on `not game_over and not game_won`
- `settings.py`: added `WIN_TIME=1200.0`, `HIT_FLASH_DURATION=0.15`, `HIT_FLASH_COLOR`, `HIT_FLASH_ALPHA_MAX=100`, `SOUND_SAMPLE_RATE`, `SOUND_CHANNELS`, `SOUND_BUFFER_SIZE`
- Tests: `tests/test_win_condition.py` (4), `tests/test_player_signals.py` (8), `tests/test_sound_manager.py` (5) — 26 total passing
- Docs: `ROADMAP.md` M7 checked off

## v0.7 — 2026-06-10
- Milestone 6: wave scaling
- `systems/wave_manager.py`: new `WaveManager` — tracks elapsed game time, exposes `params` property with `spawn_interval`, `mutant_ratio`, and `hp_mult` derived from `WAVE_TABLE`; module-level assertion enforces table is sorted ascending; active row cached in `update()` (O(1) per frame); fresh instance created per game (no reset method)
- `systems/spawner.py`: `update()` now accepts `spawn_interval`, `mutant_ratio`, and `hp_mult` as explicit params (replaces hardcoded `SPAWN_INTERVAL` import); passes `hp_mult` to both `Mutant` and `Bandit` constructors
- `entities/enemy.py`: `Bandit.__init__` and `Mutant.__init__` both accept `hp_mult=1.0`; `self.hp = int(MAX_HP * hp_mult)` — all enemy HP scales with wave
- `main.py`: instantiates `WaveManager` in `new_game()`; calls `wave_manager.update(dt)` each active frame; passes wave params to `spawner.update()`; fresh `WaveManager` on restart
- `settings.py`: `SPAWN_INTERVAL` replaced with `WAVE_TABLE` — list of `(minute_threshold, spawn_interval, mutant_ratio, hp_mult)` tuples covering 5 difficulty tiers
- Docs: `ROADMAP.md` M6 checked off

## v0.6 — 2026-06-10
- Milestone 5: XP orbs, leveling, and upgrade selection
- `entities/xp_orb.py`: new `XPOrb` sprite — 10s lifetime, proximity pickup at 20px radius, green circle r=5; calls `player.collect_xp()` on contact and self-removes via `kill()`
- `entities/enemy.py`: `take_damage()` now returns `True` on kill (for orb spawning), `False` otherwise; `Mutant` and `Bandit` gain `xp_value` attribute (5 and 10 respectively)
- `entities/player.py`: combat stats (`damage`, `move_speed`, `mag_size`, `reload_time`, `shot_cooldown_base`) promoted to mutable instance vars; `collect_xp()` accumulates XP and sets `pending_level_up` flag; `apply_upgrade()` applies one of 6 upgrades to live stats
- `entities/projectile.py`: `Bullet` accepts optional `damage` parameter so player's mutable damage stat is passed through
- `ui/hud.py`: XP bar + level label added below HP bar; ammo label reads `player.mag_size` (not hardcoded constant); `draw_level_up()` renders semi-transparent overlay with 3 upgrade cards, keyboard (1/2/3) and click input; `hovered_upgrade()` hit-tests card rects
- `main.py`: orbs spawned on enemy kill; level-up pause state (`level_up` flag) freezes `all_sprites.update` and collision handling; upgrade selection via keyboard or click; `BANDIT_FIRE_INTERVAL` halved (2.5→1.25s) for better pacing
- `settings.py`: +XP orb constants, enemy XP values, XP/level formula, 6 upgrade multipliers, `UPGRADES` list, HUD card/XP colors
- Code review fix: `collect_xp` uses `while` loop (not `if`) so multi-threshold XP overflows handle correctly; `xp_orbs` group removed (dead state — pickup handled by proximity in `XPOrb.update`)
- Docs: `ROADMAP.md` M5 checked off

## v0.5.1 — 2026-06-10
- Post-review fixes and cleanup
- `entities/enemy.py`: `_fire_timer` now resets to 0 when Bandit resumes chasing — prevents premature fire on re-entry to firing mode; extracted `Enemy` base class with shared `take_damage()`; Bandit uses precomputed `BANDIT_PREFERRED_RANGE_SQ` / `BANDIT_RESUME_CHASE_RANGE_SQ`; Bandit registers projectiles explicitly instead of relying on constructor side-effects
- `entities/projectile.py`: extracted `Projectile` base class with shared `update()` boundary logic; `Bullet` and `BanditProjectile` inherit from it; `BanditProjectile` no longer self-registers into groups (caller registers, consistent with `Bullet`)
- `settings.py`: added `BANDIT_PREFERRED_RANGE_SQ` and `BANDIT_RESUME_CHASE_RANGE_SQ` as precomputed constants
- `systems/spawner.py`: spawn ratio exposed as `mutant_ratio=0.5` parameter — M6 wave scaling can pass a time-based value without refactoring

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
