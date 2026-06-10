import pygame
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    PLAYER_DAMAGE, BULLET_SPEED, BULLET_RADIUS, BULLET_COLOR,
    BANDIT_PROJECTILE_SPEED, BANDIT_PROJECTILE_RADIUS,
    BANDIT_PROJECTILE_COLOR, BANDIT_PROJECTILE_DAMAGE,
)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed, radius, damage):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.vel = direction * speed
        self.damage = damage
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, player=None):
        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if (self.pos.x < ARENA_LEFT or self.pos.x > ARENA_RIGHT or
                self.pos.y < ARENA_TOP or self.pos.y > ARENA_BOTTOM):
            self.kill()


class Bullet(Projectile):
    def __init__(self, pos, direction, damage=PLAYER_DAMAGE):
        super().__init__(pos, direction, BULLET_SPEED, BULLET_RADIUS, damage)

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, self.rect.center, BULLET_RADIUS)


class BanditProjectile(Projectile):
    def __init__(self, pos, direction):
        super().__init__(pos, direction, BANDIT_PROJECTILE_SPEED, BANDIT_PROJECTILE_RADIUS, BANDIT_PROJECTILE_DAMAGE)

    def draw(self, surface):
        pygame.draw.circle(surface, BANDIT_PROJECTILE_COLOR, self.rect.center, BANDIT_PROJECTILE_RADIUS)
