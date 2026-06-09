# Stalker Survivor

A top-down bullet heaven set in a post-nuclear wasteland. Survive 20 minutes against endless waves of bandits and mutants.

The core mechanic is **reload timing** — deciding when to reload under pressure is the central skill expression. Mutants punish reactive reloaders hard.

Inspired by S.T.A.L.K.E.R., Vampire Survivors, and Hotline Miami.

---

## Setup

Requires Python 3.12 (pygame has a circular import bug on Python 3.14).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
source .venv/bin/activate   # if not already active
python3 main.py
```

## Controls

| Input | Action |
|-------|--------|
| WASD | Move |
| Mouse | Aim |
| Left click | Fire |
| R | Reload |
| Escape | Quit |

---

## Status

Early development — placeholder graphics. See `docs/ROADMAP.md` for milestone progress.
