import random
from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
from systems.wave_manager import WaveManager


class SurviveRoom:
    spawns_waves = True

    def __init__(self, duration, difficulty):
        self.duration = duration
        self.difficulty = difficulty
        self.mutant_ratio = random.uniform(ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX)
        self._elapsed = 0.0

    def record_kill(self):
        pass

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

    def update(self, dt):
        pass

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

    def update(self, dt):
        pass

    def record_kill(self):
        pass

    @property
    def is_complete(self):
        return False

    @property
    def timer_display(self):
        return None


class RunManager:
    def __init__(self, room_sequence):
        self._sequence = list(room_sequence)
        self._room_idx = 0
        self._run_elapsed = 0.0
        if not self._sequence:
            self._state = 'WIN'
            self._current_room = None
            self._wave_manager = None
        else:
            self._enter_room(self._sequence[0])

    def _build_room(self, defn):
        t = defn['type']
        d = defn['difficulty']
        if t == 'survive':
            return SurviveRoom(defn['duration'], d)
        if t == 'kill_count':
            return KillCountRoom(defn['target'], d)
        return BossRoom(d)

    def _enter_room(self, defn):
        self._current_room = self._build_room(defn)
        self._wave_manager = WaveManager(
            difficulty=self._current_room.difficulty,
            mutant_ratio=self._current_room.mutant_ratio,
        )
        self._state = 'ENCOUNTER'

    @property
    def state(self):
        return self._state

    @property
    def current_room(self):
        return self._current_room

    @property
    def wave_manager(self):
        return self._wave_manager

    @property
    def run_elapsed(self):
        return self._run_elapsed

    def update(self, dt):
        if self._state != 'ENCOUNTER':
            return
        self._run_elapsed += dt
        self._current_room.update(dt)
        if self._current_room.is_complete:
            if self._room_idx >= len(self._sequence) - 1:
                self._state = 'WIN'
            else:
                self._state = 'REWARD'

    def record_kill(self):
        if self._state != 'ENCOUNTER':
            return
        self._current_room.record_kill()

    def advance(self):
        if self._state != 'REWARD':
            return
        self._room_idx += 1
        if self._room_idx >= len(self._sequence):
            self._state = 'WIN'
            return
        self._enter_room(self._sequence[self._room_idx])

    def on_player_death(self):
        self._state = 'GAME_OVER'
