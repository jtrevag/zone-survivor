# Changelog

Track what changed, when, and why. Format: `## vX.X — YYYY-MM-DD`

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
