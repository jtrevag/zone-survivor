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
