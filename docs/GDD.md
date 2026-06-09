# Stalker Survivor — Game Design Document
> Version: 0.1 | Status: Pre-production

## Core Fantasy
You are a lone survivor in an irradiated wasteland, methodically holding back an endless tide. Victory comes from positioning and resource discipline — not reflexes. The primary skill expression is **reload timing**: deciding when to reload under pressure is the central tension of every encounter.

## Pillars
1. **Methodical** — Encounters reward patience and positioning over twitch reaction
2. **Tense** — The reload window is always a vulnerability; mutants punish it hard
3. **Escalating** — The world gets more dangerous faster than you get stronger

## Genre
Bullet heaven / survivor-like with manual resource management (ammo/reload). Top-down 2D.

## Aesthetic
Post-nuclear wasteland. STALKER-inspired — bleak, atmospheric, grounded. No fantasy, no neon. Muted greens, browns, grays. Pixel art (target tile size: 32x32).

## Platform
PC (keyboard + mouse). Terminal-first development workflow.

## Win / Lose
- **Win:** Survive 20 minutes
- **Lose:** HP reaches zero
- Both states show time survived and a restart option

---

## Player
| Stat | Base Value |
|------|-----------|
| Move Speed | 200 px/s |
| Max HP | 100 |
| Mag Size | 5 rounds |
| Reload Time | 2.0 seconds |
| Damage | 40 per shot |

- Faces mouse cursor at all times
- Left click to fire (manual, not auto)
- `R` to reload — cannot fire during reload
- Cannot overshoot mag (clicking on empty mag does nothing, prompts reload indicator)

## Starting Weapon: Bolt-Action Rifle
- High damage, slow fire rate
- Small mag (5 rounds) — every shot is a commitment
- Visible ammo counter and reload progress bar on HUD
- Satisfying feedback required: screen flash or recoil on shot, progress bar fill on reload

---

## Enemies

### Bandit (Human)
- Moves slowly toward player, stops at range
- Fires projectiles toward player at timed intervals
- Medium HP — takes 2-3 rifle shots
- Punishes poor positioning

### Mutant
- Fast, moves directly toward player
- Melee only — damages player on contact
- Low HP — dies in 1-2 shots
- Primary threat during reload windows

---

## Arena
- Bounded 1280x720 play area
- Hard walls at edges
- V1: Open field, simple obstacles (crates, rubble) as cover
- No camera scroll in v1 — single screen

---

## Upgrade System
On level-up, game pauses and player picks **one of three** randomly selected upgrades:

| Upgrade | Effect |
|---------|--------|
| Larger Mag | +2 rounds |
| Faster Reload | -20% reload time |
| More Damage | +25% damage |
| Move Speed | +10% speed |
| Max HP | +20 HP |
| Fire Rate | -15% shot cooldown |

---

## References
- Vampire Survivors (core loop structure)
- S.T.A.L.K.E.R. series (aesthetic, tone)
- Hotline Miami (top-down feel, lethality)
