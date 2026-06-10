from settings import WAVE_TABLE

assert all(
    WAVE_TABLE[i][0] < WAVE_TABLE[i + 1][0] for i in range(len(WAVE_TABLE) - 1)
), "WAVE_TABLE must be sorted ascending by minute threshold"


class WaveManager:
    def __init__(self):
        self._elapsed = 0.0
        self._row = WAVE_TABLE[0]
        self._next_idx = 1

    def update(self, dt):
        self._elapsed += dt
        minutes = self._elapsed / 60.0
        while self._next_idx < len(WAVE_TABLE) and minutes >= WAVE_TABLE[self._next_idx][0]:
            self._row = WAVE_TABLE[self._next_idx]
            self._next_idx += 1

    @property
    def elapsed(self):
        return self._elapsed

    @property
    def params(self):
        return {
            'spawn_interval': self._row[1],
            'mutant_ratio':   self._row[2],
            'hp_mult':        self._row[3],
        }
