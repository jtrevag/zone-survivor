from settings import BASE_SPAWN_INTERVAL, BASE_HP_MULT, DEFAULT_MUTANT_RATIO


class WaveManager:
    def __init__(self, difficulty=1.0, mutant_ratio=DEFAULT_MUTANT_RATIO):
        self._difficulty = difficulty
        self._mutant_ratio = mutant_ratio

    @property
    def params(self):
        return {
            'spawn_interval': BASE_SPAWN_INTERVAL / self._difficulty,
            'hp_mult':        BASE_HP_MULT * self._difficulty,
            'mutant_ratio':   self._mutant_ratio,
        }
