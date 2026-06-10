import pygame
from settings import (
    MUTANT_COLOR, MUTANT_SIZE, MUTANT_SPEED, MUTANT_MAX_HP,
    MUTANT_CONTACT_DAMAGE, MUTANT_CONTACT_COOLDOWN, MUTANT_XP_VALUE,
    BANDIT_COLOR, BANDIT_SIZE, BANDIT_SPEED, BANDIT_MAX_HP,
    BANDIT_PREFERRED_RANGE_SQ, BANDIT_RESUME_CHASE_RANGE_SQ, BANDIT_FIRE_INTERVAL,
    BANDIT_XP_VALUE,
)
from entities.projectile import BanditProjectile


class Enemy(pygame.sprite.Sprite):
    def take_damage(self, amount):
        if self.hp <= 0:
            return False
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.kill()
            return True
        return False


class Mutant(Enemy):
    def __init__(self, pos, hp_mult=1.0):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.hp = int(MUTANT_MAX_HP * hp_mult)
        self.xp_value = MUTANT_XP_VALUE
        self._contact_cooldown = 0.0
        self.rect = pygame.Rect(0, 0, MUTANT_SIZE, MUTANT_SIZE)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, player=None):
        if player is None or player.dead:
            return

        to_player = player.pos - self.pos
        if to_player.length_squared() > 0:
            to_player.normalize_ip()
            self.pos += to_player * MUTANT_SPEED * dt

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if self._contact_cooldown > 0:
            self._contact_cooldown = max(0.0, self._contact_cooldown - dt)

        if self.rect.colliderect(player.rect) and self._contact_cooldown <= 0:
            player.take_damage(MUTANT_CONTACT_DAMAGE)
            self._contact_cooldown = MUTANT_CONTACT_COOLDOWN

    def draw(self, surface):
        pygame.draw.rect(surface, MUTANT_COLOR, self.rect)


class Bandit(Enemy):
    def __init__(self, pos, all_sprites, enemy_projectiles, hp_mult=1.0):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.hp = int(BANDIT_MAX_HP * hp_mult)
        self.xp_value = BANDIT_XP_VALUE
        self._all_sprites = all_sprites
        self._enemy_projectiles = enemy_projectiles
        self._chasing = True
        self._fire_timer = 0.0
        self.rect = pygame.Rect(0, 0, BANDIT_SIZE, BANDIT_SIZE)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, player=None):
        if player is None or player.dead:
            return

        to_player = player.pos - self.pos
        dist_sq = to_player.length_squared()
        if dist_sq == 0:
            return

        if self._chasing and dist_sq <= BANDIT_PREFERRED_RANGE_SQ:
            self._chasing = False
        elif not self._chasing and dist_sq > BANDIT_RESUME_CHASE_RANGE_SQ:
            self._chasing = True
            self._fire_timer = 0.0

        if self._chasing:
            self.pos += to_player.normalize() * BANDIT_SPEED * dt
        else:
            self._fire_timer += dt
            if self._fire_timer >= BANDIT_FIRE_INTERVAL:
                self._fire_timer = 0.0
                proj = BanditProjectile(self.pos, to_player.normalize())
                self._all_sprites.add(proj)
                self._enemy_projectiles.add(proj)

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface):
        pygame.draw.rect(surface, BANDIT_COLOR, self.rect)
