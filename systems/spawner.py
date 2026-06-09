import random
from settings import (
    ARENA_LEFT, ARENA_TOP, ARENA_RIGHT, ARENA_BOTTOM,
    SPAWN_INTERVAL,
)
from entities.enemy import Mutant


class Spawner:
    def __init__(self):
        self._timer = 0.0

    def update(self, dt, all_sprites, enemies):
        self._timer += dt
        if self._timer >= SPAWN_INTERVAL:
            self._timer -= SPAWN_INTERVAL
            pos = self._random_edge_pos()
            mutant = Mutant(pos)
            all_sprites.add(mutant)
            enemies.add(mutant)

    def _random_edge_pos(self):
        return random.choice([
            (random.randint(ARENA_LEFT, ARENA_RIGHT - 1), ARENA_TOP),
            (random.randint(ARENA_LEFT, ARENA_RIGHT - 1), ARENA_BOTTOM),
            (ARENA_LEFT,  random.randint(ARENA_TOP, ARENA_BOTTOM - 1)),
            (ARENA_RIGHT, random.randint(ARENA_TOP, ARENA_BOTTOM - 1)),
        ])
