import pygame
from settings import (
    MUTANT_COLOR, MUTANT_SIZE, MUTANT_SPEED, MUTANT_MAX_HP,
    MUTANT_CONTACT_DAMAGE, MUTANT_CONTACT_COOLDOWN,
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
