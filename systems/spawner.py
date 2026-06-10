import random
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    SPAWN_INTERVAL,
)
from entities.enemy import Mutant, Bandit


class Spawner:
    def __init__(self):
        self._timer = 0.0

    def update(self, dt, all_sprites, enemies, enemy_projectiles, mutant_ratio=0.5):
        self._timer += dt
        if self._timer >= SPAWN_INTERVAL:
            self._timer -= SPAWN_INTERVAL
            pos = self._random_edge_pos()
            if random.random() < mutant_ratio:
                enemy = Mutant(pos)
            else:
                enemy = Bandit(pos, all_sprites, enemy_projectiles)
            all_sprites.add(enemy)
            enemies.add(enemy)

    def _random_edge_pos(self):
        return random.choice([
            (random.randint(ARENA_LEFT, ARENA_RIGHT - 1), ARENA_TOP),
            (random.randint(ARENA_LEFT, ARENA_RIGHT - 1), ARENA_BOTTOM),
            (ARENA_LEFT,  random.randint(ARENA_TOP, ARENA_BOTTOM - 1)),
            (ARENA_RIGHT, random.randint(ARENA_TOP, ARENA_BOTTOM - 1)),
        ])
