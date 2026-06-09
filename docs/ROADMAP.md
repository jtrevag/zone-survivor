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

## Milestone 2 — Combat Basics
- [ ] Left click fires a bullet toward mouse cursor
- [ ] Bullet travels and despawns at arena edge
- [ ] Ammo counter decrements on fire
- [ ] Empty-click does nothing (no fire at 0 ammo)
- [ ] R key initiates reload with timer
- [ ] Cannot fire during reload
- [ ] HUD: ammo counter + reload progress bar

---

## Milestone 3 — First Enemy (Mutant)
- [ ] Mutants spawn at arena edges
- [ ] Mutants chase player directly
- [ ] Player bullets hit and kill mutants
- [ ] Mutants deal contact damage to player
- [ ] Player HP displayed on HUD
- [ ] Player death state (game over screen, restart)

---

## Milestone 4 — Second Enemy (Bandit)
- [ ] Bandits spawn and pathfind toward player
- [ ] Bandits stop at preferred range and fire
- [ ] Bandit projectiles travel and damage player
- [ ] Both enemy types active simultaneously

---

## Milestone 5 — XP & Leveling
- [ ] Enemies drop XP orbs on death
- [ ] Player collects orbs on contact
- [ ] XP bar on HUD
- [ ] Level-up screen pauses game
- [ ] 3 random upgrades offered, player picks one
- [ ] Upgrades apply correctly to player stats

---

## Milestone 6 — Wave Scaling
- [ ] Wave manager ticks on 60s intervals
- [ ] Spawn rate increases per wave table
- [ ] Mutant ratio increases over time
- [ ] Bandit HP scales after minute 5

---

## Milestone 7 — Win Condition & Polish Pass
- [ ] 20-minute survival timer on HUD
- [ ] Win screen on timer completion
- [ ] Death screen shows time survived
- [ ] Restart works cleanly from both screens
- [ ] Basic sound effects (gunshot, reload, hit, death)
- [ ] Screen flash on player hit

---

## Post-v1 (Backlog)
- Additional weapons (shotgun, SMG with auto-fire but more reloads)
- Cover/obstacles in arena
- Elite enemy variants
- Persistent upgrade tree between runs
- Tilemap / real art assets
- Controller support
