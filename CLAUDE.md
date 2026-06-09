# CLAUDE.md — Stalker Survivor

## Project
Top-down bullet heaven in Python/Pygame. STALKER-inspired post-nuclear aesthetic.
Core mechanic: manual reload timing as primary skill expression.

## Docs
- `docs/GDD.md` — core design, pillars, win/lose
- `docs/MECHANICS.md` — precise rules for all systems
- `docs/ENTITIES.md` — all entity stats and behaviors
- `docs/ROADMAP.md` — milestone build order (always check current milestone)
- `docs/CHANGELOG.md` — update this after every meaningful change

## Commands
- Run game: `python main.py`
- Install deps: `pip install -r requirements.txt`

## Project Structure
```
stalker-survivor/
├── main.py           # Game loop only — no logic here
├── settings.py       # All constants and tuning values
├── entities/
│   ├── player.py
│   ├── enemy.py
│   └── projectile.py
├── systems/
│   ├── spawner.py
│   ├── wave_manager.py
│   └── xp_system.py
├── ui/
│   └── hud.py
└── docs/
```

## Code Rules
- All magic numbers go in `settings.py` — never hardcode values inline
- `main.py` contains only the game loop — no entity or system logic
- Use pygame sprite groups for all entities
- Comment non-obvious logic; no comments on self-evident code
- Target 60 FPS

## Placeholders (no art assets yet)
- Player: white circle r=16
- Bandit: blue rect 24x24
- Mutant: red rect 20x20
- Player bullet: yellow circle r=4
- Bandit projectile: orange circle r=3
- XP orb: green circle r=5

## Current Build Status
Check `docs/ROADMAP.md` for active milestone before starting any session.
Do not implement features beyond the current milestone.

## Documentation Sync
Keep docs in sync with code at all times — they are the source of truth, not the code.
- Any stat, behavior, or rule change → update the relevant doc (`ENTITIES.md`, `MECHANICS.md`, etc.) in the same commit
- Any new system or mechanic added → document it before or alongside implementation
- If a design decision is made during a session (e.g. tuning a value, changing behavior), update the doc immediately — do not defer to a later pass
- `docs/GDD.md` reflects the current intended game, not the original spec

## Git
- Commit after each milestone is complete
- Format: `feat: milestone N — <description>`
- Update `docs/CHANGELOG.md` with every commit — note what changed and why
