import math
import pygame
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    BANDIT_PROJECTILE_SPEED, BANDIT_PROJECTILE_RADIUS,
    BANDIT_PROJECTILE_COLOR, BANDIT_PROJECTILE_DAMAGE,
)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, speed, radius, damage):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.vel = direction * speed
        self.damage = damage
        self.radius = radius
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, player=None):
        self.pos += self.vel * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        if (self.pos.x < ARENA_LEFT or self.pos.x > ARENA_RIGHT or
                self.pos.y < ARENA_TOP or self.pos.y > ARENA_BOTTOM):
            self.kill()


class Bullet(Projectile):
    def __init__(self, pos, direction, damage, radius, color, shape, speed,
                 pierce_count=0, pierce_damage_mult=0.5):
        super().__init__(pos, direction, speed, radius, damage)
        self.color = color
        self.shape = shape
        self.pierce_count = pierce_count
        self.pierce_damage_mult = pierce_damage_mult

    def on_hit(self, enemy):
        """Deal damage to enemy. Returns True if bullet should die, False if it pierces."""
        enemy.take_damage(self.damage)
        if self.pierce_count > 0:
            self.damage = int(self.damage * self.pierce_damage_mult)
            self.pierce_count -= 1
            return False
        return True

    def draw(self, surface):
        if self.shape == 'circle':
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius)
        elif self.shape == 'rect':
            cx, cy = self.rect.center
            angle = math.atan2(self.vel.y, self.vel.x)
            hl = self.radius * 2
            hw = max(1, self.radius // 2)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            pts = [
                (cx + cos_a * hl - sin_a * hw, cy + sin_a * hl + cos_a * hw),
                (cx + cos_a * hl + sin_a * hw, cy + sin_a * hl - cos_a * hw),
                (cx - cos_a * hl + sin_a * hw, cy - sin_a * hl - cos_a * hw),
                (cx - cos_a * hl - sin_a * hw, cy - sin_a * hl + cos_a * hw),
            ]
            pygame.draw.polygon(surface, self.color, pts)


class BanditProjectile(Projectile):
    def __init__(self, pos, direction):
        super().__init__(pos, direction, BANDIT_PROJECTILE_SPEED, BANDIT_PROJECTILE_RADIUS, BANDIT_PROJECTILE_DAMAGE)

    def draw(self, surface):
        pygame.draw.circle(surface, BANDIT_PROJECTILE_COLOR, self.rect.center, self.radius)
