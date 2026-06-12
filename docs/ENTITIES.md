# Entities Reference

## Player

**Placeholder:** White circle, radius 16px

| Property | Value |
|----------|-------|
| move_speed | 200 px/s |
| max_hp | 100 |
| hp | 100 |
| weapon | pistol (default) |
| mag_size | set by equipped weapon |
| ammo | set by equipped weapon |
| reload_time | set by equipped weapon |
| is_reloading | false |
| reload_progress | 0.0–1.0 |
| damage | set by equipped weapon |
| shot_cooldown | set by equipped weapon |
| augments | [] (empty at start) |

**States:** idle, moving, firing, reloading, dead

---

## Bandit

**Placeholder:** Blue rectangle, 24x24px

| Property | Value |
|----------|-------|
| move_speed | 60 px/s |
| max_hp | 80 |
| preferred_range | 250px |
| fire_interval | 1.25s |
| projectile_speed | 180 px/s |
| projectile_damage | 12 |
| xp_value | 10 |

**Behavior:**
1. Move toward player until within `preferred_range`
2. Stop and fire at player every `fire_interval`
3. If player moves outside `preferred_range + 50px`, resume chasing

---

## Mutant

**Placeholder:** Red rectangle, 20x20px

| Property | Value |
|----------|-------|
| move_speed | 140 px/s |
|max_hp | 35 |
| contact_damage | 15 |
| contact_cooldown | 0.5s |
| xp_value | 5 |

**Behavior:**
1. Always move directly toward player
2. Deal damage on contact, respecting cooldown
3. Never stop

---

## Projectiles

### Pistol Bullet
**Placeholder:** Yellow circle, radius 4px

| Property | Value |
|----------|-------|
| speed | 500 px/s |
| damage | 55 (player.damage) |
| pellets | 1 |
| spread | 0° |
| shape | circle |
| lifetime | until hit or out of bounds |

### Shotgun Pellet
**Placeholder:** Orange circle, radius 4px

| Property | Value |
|----------|-------|
| speed | 500 px/s |
| damage | 20 per pellet (×4 pellets) |
| pellets | 4 |
| spread | 25° cone |
| shape | circle |
| lifetime | until hit or out of bounds |

### Bandit Projectile
**Placeholder:** Orange circle, radius 3px

| Property | Value |
|----------|-------|
| speed | 180 px/s |
| damage | 12 |
| lifetime | until hit or out of bounds |

---

## XP Orb

**Placeholder:** Green circle, radius 5px

| Property | Value |
|----------|-------|
| value | depends on source enemy |
| lifetime | 10 seconds |
| pickup_radius | 20px (player center to orb center) |
