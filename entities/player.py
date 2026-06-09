import pygame
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    WHITE, INDICATOR_COLOR,
    PLAYER_SPEED, PLAYER_RADIUS, PLAYER_INDICATOR_LENGTH,
    PLAYER_MAX_HP, PLAYER_MAG_SIZE, PLAYER_RELOAD_TIME, PLAYER_SHOT_COOLDOWN,
)
from entities.projectile import Bullet


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(
            (ARENA_LEFT + ARENA_RIGHT) / 2,
            (ARENA_TOP + ARENA_BOTTOM) / 2,
        )
        self.facing = pygame.math.Vector2(1, 0)  # normalized direction toward mouse
        self._move = pygame.math.Vector2()  # reused to avoid 60Hz allocation
        self.rect = pygame.Rect(0, 0, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.dead = False
        self.ammo = PLAYER_MAG_SIZE
        self.reloading = False
        self.reload_progress = 0.0   # 0.0 → 1.0
        self._shot_cooldown = 0.0    # seconds remaining until next shot allowed

    def take_damage(self, amount):
        if self.dead:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.dead = True

    def try_fire(self):
        """Return a Bullet if firing is allowed, else None."""
        if self.reloading or self._shot_cooldown > 0 or self.ammo <= 0:
            return None
        self.ammo -= 1
        self._shot_cooldown = PLAYER_SHOT_COOLDOWN
        return Bullet(self.pos, self.facing)

    def try_reload(self):
        """Start reload if not already reloading."""
        if not self.reloading:
            self.reloading = True
            self.reload_progress = 0.0

    def update(self, dt, player=None):
        keys = pygame.key.get_pressed()
        self._move.update(keys[pygame.K_d] - keys[pygame.K_a],
                          keys[pygame.K_s] - keys[pygame.K_w])
        if self._move.length_squared() > 0:
            self._move.normalize_ip()
            self.pos += self._move * PLAYER_SPEED * dt

        # Clamp so circle edge stays inside arena
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
            self.reload_progress = min(1.0, self.reload_progress + dt / PLAYER_RELOAD_TIME)
            if self.reload_progress >= 1.0:
                self.ammo = PLAYER_MAG_SIZE
                self.reloading = False

    def draw(self, surface):
        center = self.rect.center
        pygame.draw.circle(surface, WHITE, center, PLAYER_RADIUS)
        tip = pygame.math.Vector2(center) + self.facing * PLAYER_INDICATOR_LENGTH
        pygame.draw.line(surface, INDICATOR_COLOR, center, tip, 2)
