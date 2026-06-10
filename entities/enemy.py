import pygame
from settings import (
    MUTANT_COLOR, MUTANT_SIZE, MUTANT_SPEED, MUTANT_MAX_HP,
    MUTANT_CONTACT_DAMAGE, MUTANT_CONTACT_COOLDOWN,
    BANDIT_COLOR, BANDIT_SIZE, BANDIT_SPEED, BANDIT_MAX_HP,
    BANDIT_PREFERRED_RANGE, BANDIT_RESUME_CHASE_RANGE, BANDIT_FIRE_INTERVAL,
)


class Mutant(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.hp = MUTANT_MAX_HP
        self._contact_cooldown = 0.0
        self.rect = pygame.Rect(0, 0, MUTANT_SIZE, MUTANT_SIZE)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def take_damage(self, amount):
        if self.hp <= 0:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.kill()

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


class Bandit(pygame.sprite.Sprite):
    def __init__(self, pos, all_sprites, bandit_projectiles):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.hp = BANDIT_MAX_HP
        self._all_sprites = all_sprites
        self._bandit_projectiles = bandit_projectiles
        self._chasing = True
        self._fire_timer = 0.0
        self.rect = pygame.Rect(0, 0, BANDIT_SIZE, BANDIT_SIZE)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def take_damage(self, amount):
        if self.hp <= 0:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.kill()

    def update(self, dt, player=None):
        if player is None or player.dead:
            return

        from entities.projectile import BanditProjectile

        to_player = player.pos - self.pos
        dist = to_player.length()

        if self._chasing and dist <= BANDIT_PREFERRED_RANGE:
            self._chasing = False
        elif not self._chasing and dist > BANDIT_RESUME_CHASE_RANGE:
            self._chasing = True

        if self._chasing:
            if dist > 0:
                self.pos += to_player / dist * BANDIT_SPEED * dt
        else:
            self._fire_timer += dt
            if self._fire_timer >= BANDIT_FIRE_INTERVAL:
                self._fire_timer = 0.0
                if dist > 0:
                    direction = to_player / dist
                    BanditProjectile(self.pos, direction, self._all_sprites, self._bandit_projectiles)

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface):
        pygame.draw.rect(surface, BANDIT_COLOR, self.rect)
