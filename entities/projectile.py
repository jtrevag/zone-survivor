import pygame
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    PLAYER_DAMAGE, BULLET_SPEED, BULLET_RADIUS, BULLET_COLOR,
    BANDIT_PROJECTILE_SPEED, BANDIT_PROJECTILE_RADIUS,
    BANDIT_PROJECTILE_COLOR, BANDIT_PROJECTILE_DAMAGE,
)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.vel = direction * BULLET_SPEED
        self.damage = PLAYER_DAMAGE
        self.rect = pygame.Rect(0, 0, BULLET_RADIUS * 2, BULLET_RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, player=None):
        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if (self.pos.x < ARENA_LEFT or self.pos.x > ARENA_RIGHT or
                self.pos.y < ARENA_TOP or self.pos.y > ARENA_BOTTOM):
            self.kill()

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, self.rect.center, BULLET_RADIUS)


class BanditProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, all_sprites, bandit_projectiles):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.vel = direction * BANDIT_PROJECTILE_SPEED
        self.damage = BANDIT_PROJECTILE_DAMAGE
        self.rect = pygame.Rect(0, 0, BANDIT_PROJECTILE_RADIUS * 2, BANDIT_PROJECTILE_RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        all_sprites.add(self)
        bandit_projectiles.add(self)

    def update(self, dt, player=None):
        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if (self.pos.x < ARENA_LEFT or self.pos.x > ARENA_RIGHT or
                self.pos.y < ARENA_TOP or self.pos.y > ARENA_BOTTOM):
            self.kill()

    def draw(self, surface):
        pygame.draw.circle(surface, BANDIT_PROJECTILE_COLOR, self.rect.center, BANDIT_PROJECTILE_RADIUS)
