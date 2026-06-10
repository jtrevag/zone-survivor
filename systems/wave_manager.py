from settings import WAVE_TABLE


class WaveManager:
    def __init__(self):
        self._elapsed = 0.0

    def reset(self):
        self._elapsed = 0.0

    def update(self, dt):
        self._elapsed += dt

    @property
    def params(self):
        minutes = self._elapsed / 60.0
        row = WAVE_TABLE[0]
        for entry in WAVE_TABLE:
            if minutes >= entry[0]:
                row = entry
        return {
            'spawn_interval': row[1],
            'mutant_ratio':   row[2],
            'bandit_hp_mult': row[3],
        }
