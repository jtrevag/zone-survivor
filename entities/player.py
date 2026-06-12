import math
import pygame
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    WHITE, INDICATOR_COLOR,
    PLAYER_SPEED, PLAYER_RADIUS, PLAYER_INDICATOR_LENGTH,
    PLAYER_MAX_HP,
    WEAPONS,
    XP_PER_LEVEL_BASE,
    UPGRADE_MAG_BONUS, UPGRADE_RELOAD_MULT, UPGRADE_DAMAGE_MULT,
    UPGRADE_SPEED_MULT, UPGRADE_HP_BONUS, UPGRADE_FIRE_RATE_MULT,
    HIT_FLASH_DURATION,
)
from entities.projectile import Bullet

# Upgrade IDs that scale with the active weapon and must be replayed after equip.
# 'speed' and 'hp' are player-wide and never reset, so they are excluded.
_WEAPON_UPGRADE_IDS = frozenset({'mag', 'reload', 'damage', 'fire_rate'})


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(
            (ARENA_LEFT + ARENA_RIGHT) / 2,
            (ARENA_TOP + ARENA_BOTTOM) / 2,
        )
        self.facing = pygame.math.Vector2(1, 0)
        self._move = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.dead = False

        self.move_speed = PLAYER_SPEED

        self.reloading = False
        self.reload_progress = 0.0
        self._shot_cooldown = 0.0

        # XP / leveling
        self.xp = 0
        self.level = 1
        self.xp_to_next = XP_PER_LEVEL_BASE
        self.pending_level_up = False

        self.hit_flash_timer = 0.0
        self.just_hit = False
        self.reload_complete = False

        self._ammo_by_weapon = {}   # weapon name → saved ammo
        self._upgrade_history = []  # ordered list of applied upgrade IDs
        self.equip(WEAPONS['pistol'])

    def equip(self, weapon_def):
        # Persist current weapon's ammo before switching
        if hasattr(self, 'weapon'):
            self._ammo_by_weapon[self.weapon['name']] = self.ammo

        self.weapon = weapon_def
        self.mag_size = weapon_def['mag_size']
        self.reload_time = weapon_def['reload_time']
        self.shot_cooldown_base = weapon_def['shot_cooldown']
        self.damage = weapon_def['damage']
        self.reloading = False
        self.reload_progress = 0.0
        self.augments = []

        # Replay weapon-specific upgrades on top of the new weapon's base stats
        for uid in self._upgrade_history:
            if uid in _WEAPON_UPGRADE_IDS:
                self._apply_one_upgrade(uid)

        # Restore saved ammo (or full mag if first equip), clamped to current mag_size
        self.ammo = min(
            self._ammo_by_weapon.get(weapon_def['name'], self.mag_size),
            self.mag_size,
        )

    def heal(self, fraction):
        self.hp = min(self.max_hp, self.hp + int(self.max_hp * fraction))

    def take_damage(self, amount):
        if self.dead:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.dead = True
        else:
            self.just_hit = True
        self.hit_flash_timer = HIT_FLASH_DURATION

    def collect_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = XP_PER_LEVEL_BASE * self.level
            self.pending_level_up = True

    def apply_upgrade(self, upgrade_id):
        self._upgrade_history.append(upgrade_id)
        self._apply_one_upgrade(upgrade_id)

    def _apply_one_upgrade(self, upgrade_id):
        if upgrade_id == 'mag':
            self.mag_size += UPGRADE_MAG_BONUS
            self.ammo = min(self.ammo + UPGRADE_MAG_BONUS, self.mag_size)
        elif upgrade_id == 'reload':
            self.reload_time *= UPGRADE_RELOAD_MULT
        elif upgrade_id == 'damage':
            self.damage = int(self.damage * UPGRADE_DAMAGE_MULT)
        elif upgrade_id == 'speed':
            self.move_speed *= UPGRADE_SPEED_MULT
        elif upgrade_id == 'hp':
            self.max_hp += UPGRADE_HP_BONUS
            self.hp = min(self.hp + UPGRADE_HP_BONUS, self.max_hp)
        elif upgrade_id == 'fire_rate':
            self.shot_cooldown_base *= UPGRADE_FIRE_RATE_MULT

    def try_fire(self):
        """Return list of Bullets; empty list means cannot fire."""
        if self.reloading or self._shot_cooldown > 0 or self.ammo <= 0:
            return []
        self.ammo -= 1
        self._shot_cooldown = self.shot_cooldown_base

        weapon = self.weapon
        pellets = self.effective_pellets()
        spread = weapon['spread']
        bdef = weapon['bullet']
        pierce_count, pierce_damage_mult = self.effective_pierce()

        if pellets == 1 or spread == 0.0:
            directions = [pygame.math.Vector2(self.facing)]
        else:
            base_angle = math.degrees(math.atan2(self.facing.y, self.facing.x))
            half = spread / 2.0
            step = spread / (pellets - 1)
            directions = [
                pygame.math.Vector2(
                    math.cos(math.radians(base_angle - half + step * i)),
                    math.sin(math.radians(base_angle - half + step * i)),
                )
                for i in range(pellets)
            ]

        return [
            Bullet(
                self.pos, d, self.effective_damage(),
                bdef['radius'], bdef['color'], bdef['shape'], bdef['speed'],
                pierce_count=pierce_count, pierce_damage_mult=pierce_damage_mult,
            )
            for d in directions
        ]

    def equip_augment(self, augment_def):
        if len(self.augments) < 2:
            self.augments.append(augment_def)

    def effective_damage(self):
        m = 1.0
        for a in self.augments:
            m *= a.get('damage_mult', 1.0)
        return int(self.damage * m)

    def effective_reload_time(self):
        m = 1.0
        for a in self.augments:
            m *= a.get('reload_time_mult', 1.0)
        return self.reload_time * m

    def effective_mag_size(self):
        m = 1.0
        for a in self.augments:
            m *= a.get('mag_size_mult', 1.0)
        return int(self.mag_size * m)

    def effective_pellets(self):
        bonus = sum(a.get('pellet_bonus', 0) for a in self.augments)
        return self.weapon['pellets'] + bonus

    def effective_pierce(self):
        for a in self.augments:
            if 'pierce_count' in a:
                return a['pierce_count'], a.get('pierce_damage_mult', 0.5)
        return 0, 0.5

    def try_reload(self):
        if not self.reloading:
            self.reloading = True
            self.reload_progress = 0.0

    def update(self, dt, player=None):
        keys = pygame.key.get_pressed()
        self._move.update(keys[pygame.K_d] - keys[pygame.K_a],
                          keys[pygame.K_s] - keys[pygame.K_w])
        if self._move.length_squared() > 0:
            self._move.normalize_ip()
            self.pos += self._move * self.move_speed * dt

        self.pos.x = max(ARENA_LEFT + PLAYER_RADIUS, min(ARENA_RIGHT - PLAYER_RADIUS, self.pos.x))
        self.pos.y = max(ARENA_TOP + PLAYER_RADIUS, min(ARENA_BOTTOM - PLAYER_RADIUS, self.pos.y))

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        to_mouse = pygame.math.Vector2(pygame.mouse.get_pos()) - self.pos
        if to_mouse.length_squared() > 0:
            to_mouse.normalize_ip()
            self.facing.update(to_mouse)

        if self._shot_cooldown > 0:
            self._shot_cooldown = max(0.0, self._shot_cooldown - dt)

        if self.reloading:
            self.reload_progress = min(1.0, self.reload_progress + dt / self.effective_reload_time())
            if self.reload_progress >= 1.0:
                self.ammo = self.effective_mag_size()
                self.reloading = False
                self.reload_complete = True

    def draw(self, surface):
        center = self.rect.center
        pygame.draw.circle(surface, WHITE, center, PLAYER_RADIUS)
        tip = pygame.math.Vector2(center) + self.facing * PLAYER_INDICATOR_LENGTH
        pygame.draw.line(surface, INDICATOR_COLOR, center, tip, 2)
