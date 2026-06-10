import pygame
from settings import XP_ORB_COLOR, XP_ORB_RADIUS, XP_ORB_LIFETIME, XP_ORB_PICKUP_RADIUS_SQ


class XPOrb(pygame.sprite.Sprite):
    def __init__(self, pos, value):
        super().__init__()
        self.pos = pygame.math.Vector2(pos)
        self.value = value
        self._lifetime = XP_ORB_LIFETIME
        self.rect = pygame.Rect(0, 0, XP_ORB_RADIUS * 2, XP_ORB_RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, dt, player=None):
        self._lifetime -= dt
        if self._lifetime <= 0:
            self.kill()
            return
        if player and not player.dead:
            if (player.pos - self.pos).length_squared() <= XP_ORB_PICKUP_RADIUS_SQ:
                player.collect_xp(self.value)
                self.kill()

    def draw(self, surface):
        pygame.draw.circle(surface, XP_ORB_COLOR, (int(self.pos.x), int(self.pos.y)), XP_ORB_RADIUS)
