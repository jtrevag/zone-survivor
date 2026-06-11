import random
from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX


class SurviveRoom:
    spawns_waves = True

    def __init__(self, duration, difficulty):
        self.duration = duration
        self.difficulty = difficulty
        self.mutant_ratio = random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)
        self._elapsed = 0.0

    def update(self, dt):
        self._elapsed += dt

    @property
    def is_complete(self):
        return self._elapsed >= self.duration

    @property
    def time_remaining(self):
        return max(0.0, self.duration - self._elapsed)

    @property
    def timer_display(self):
        return f'{int(self.time_remaining)}s'


class KillCountRoom:
    spawns_waves = True

    def __init__(self, target, difficulty):
        self.target = target
        self.difficulty = difficulty
        self.mutant_ratio = random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)
        self._kills = 0

    def record_kill(self):
        self._kills += 1

    @property
    def is_complete(self):
        return self._kills >= self.target

    @property
    def kills_remaining(self):
        return max(0, self.target - self._kills)

    @property
    def timer_display(self):
        return f'{self.kills_remaining} kills left'


class BossRoom:
    spawns_waves = False

    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.mutant_ratio = random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)

    @property
    def is_complete(self):
        return False

    @property
    def timer_display(self):
        return None
