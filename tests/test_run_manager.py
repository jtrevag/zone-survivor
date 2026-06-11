import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSurviveRoom(unittest.TestCase):
    def _make(self, duration=90, difficulty=1.0):
        from systems.run_manager import SurviveRoom
        return SurviveRoom(duration, difficulty)

    def test_not_complete_initially(self):
        r = self._make()
        self.assertFalse(r.is_complete)

    def test_complete_after_duration(self):
        r = self._make(duration=90)
        r.update(90.1)
        self.assertTrue(r.is_complete)

    def test_not_complete_just_before_duration(self):
        r = self._make(duration=90)
        r.update(89.9)
        self.assertFalse(r.is_complete)

    def test_time_remaining(self):
        r = self._make(duration=90)
        r.update(30)
        self.assertAlmostEqual(r.time_remaining, 60.0)

    def test_timer_display_shows_seconds(self):
        r = self._make(duration=90)
        r.update(30)
        self.assertEqual(r.timer_display, '60s')

    def test_spawns_waves(self):
        r = self._make()
        self.assertTrue(r.spawns_waves)

    def test_mutant_ratio_within_bounds(self):
        from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
        for _ in range(20):
            r = self._make()
            self.assertGreaterEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MIN)
            self.assertLessEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MAX)

    def test_difficulty_stored(self):
        r = self._make(difficulty=1.8)
        self.assertAlmostEqual(r.difficulty, 1.8)


class TestKillCountRoom(unittest.TestCase):
    def _make(self, target=25, difficulty=1.4):
        from systems.run_manager import KillCountRoom
        return KillCountRoom(target, difficulty)

    def test_not_complete_initially(self):
        r = self._make()
        self.assertFalse(r.is_complete)

    def test_complete_at_target(self):
        r = self._make(target=3)
        r.record_kill()
        r.record_kill()
        r.record_kill()
        self.assertTrue(r.is_complete)

    def test_not_complete_before_target(self):
        r = self._make(target=3)
        r.record_kill()
        r.record_kill()
        self.assertFalse(r.is_complete)

    def test_kills_remaining(self):
        r = self._make(target=25)
        r.record_kill()
        self.assertEqual(r.kills_remaining, 24)

    def test_timer_display_shows_kills_remaining(self):
        r = self._make(target=25)
        r.record_kill()
        self.assertEqual(r.timer_display, '24 kills left')

    def test_spawns_waves(self):
        r = self._make()
        self.assertTrue(r.spawns_waves)

    def test_mutant_ratio_within_bounds(self):
        from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
        for _ in range(20):
            r = self._make()
            self.assertGreaterEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MIN)
            self.assertLessEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MAX)


class TestBossRoom(unittest.TestCase):
    def _make(self, difficulty=2.5):
        from systems.run_manager import BossRoom
        return BossRoom(difficulty)

    def test_never_complete(self):
        r = self._make()
        self.assertFalse(r.is_complete)

    def test_no_wave_spawning(self):
        r = self._make()
        self.assertFalse(r.spawns_waves)

    def test_timer_display_is_none(self):
        r = self._make()
        self.assertIsNone(r.timer_display)

    def test_mutant_ratio_within_bounds(self):
        from settings import ROOM_MUTANT_RATIO_MIN, ROOM_MUTANT_RATIO_MAX
        for _ in range(20):
            r = self._make()
            self.assertGreaterEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MIN)
            self.assertLessEqual(r.mutant_ratio, ROOM_MUTANT_RATIO_MAX)


class TestRunManager(unittest.TestCase):
    def _sequence(self):
        return [
            {'type': 'survive', 'duration': 90, 'difficulty': 1.0},
            {'type': 'survive', 'duration': 60, 'difficulty': 1.8},
        ]

    def _make(self, sequence=None):
        from systems.run_manager import RunManager
        return RunManager(sequence if sequence is not None else self._sequence())

    def test_starts_in_encounter(self):
        rm = self._make()
        self.assertEqual(rm.state, 'ENCOUNTER')

    def test_empty_sequence_wins_immediately(self):
        rm = self._make([])
        self.assertEqual(rm.state, 'WIN')

    def test_current_room_is_first_room(self):
        from systems.run_manager import SurviveRoom
        rm = self._make()
        self.assertIsInstance(rm.current_room, SurviveRoom)

    def test_wave_manager_initialised_with_room_difficulty(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.8}])
        self.assertAlmostEqual(rm.wave_manager._difficulty, 1.8)

    def test_wave_manager_initialised_with_room_mutant_ratio(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.0}])
        self.assertAlmostEqual(rm.wave_manager._mutant_ratio, rm.current_room.mutant_ratio)

    def test_transitions_to_reward_when_room_complete(self):
        rm = self._make([{'type': 'survive', 'duration': 1, 'difficulty': 1.0}])
        rm.update(1.1)
        self.assertEqual(rm.state, 'REWARD')

    def test_does_not_complete_before_duration(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.0}])
        rm.update(89.9)
        self.assertEqual(rm.state, 'ENCOUNTER')

    def test_advance_loads_next_room(self):
        from systems.run_manager import SurviveRoom
        seq = [
            {'type': 'survive',    'duration': 1,  'difficulty': 1.0},
            {'type': 'survive',    'duration': 60, 'difficulty': 1.8},
        ]
        rm = self._make(seq)
        rm.update(1.1)  # room 1 completes → REWARD
        rm.advance()
        self.assertEqual(rm.state, 'ENCOUNTER')
        self.assertAlmostEqual(rm.current_room.duration, 60)

    def test_advance_on_last_room_sets_win(self):
        rm = self._make([{'type': 'survive', 'duration': 1, 'difficulty': 1.0}])
        rm.update(1.1)
        rm.advance()
        self.assertEqual(rm.state, 'WIN')

    def test_player_death_sets_game_over(self):
        rm = self._make()
        rm.on_player_death()
        self.assertEqual(rm.state, 'GAME_OVER')

    def test_run_elapsed_accumulates(self):
        rm = self._make()
        rm.update(1.0)
        rm.update(2.0)
        self.assertAlmostEqual(rm.run_elapsed, 3.0)

    def test_run_elapsed_pauses_in_reward(self):
        rm = self._make([{'type': 'survive', 'duration': 1, 'difficulty': 1.0}])
        rm.update(1.1)   # → REWARD; run_elapsed = 1.1
        elapsed_at_reward = rm.run_elapsed
        rm.update(5.0)   # REWARD state — should not tick elapsed
        self.assertAlmostEqual(rm.run_elapsed, elapsed_at_reward)

    def test_record_kill_delegates_to_kill_count_room(self):
        rm = self._make([{'type': 'kill_count', 'target': 1, 'difficulty': 1.0}])
        rm.record_kill()
        rm.update(0.0)
        self.assertEqual(rm.state, 'REWARD')

    def test_record_kill_ignored_for_survive_room(self):
        rm = self._make([{'type': 'survive', 'duration': 90, 'difficulty': 1.0}])
        rm.record_kill()  # should not raise
        self.assertEqual(rm.state, 'ENCOUNTER')

    def test_kill_count_room_built_from_sequence(self):
        from systems.run_manager import KillCountRoom
        rm = self._make([{'type': 'kill_count', 'target': 25, 'difficulty': 1.4}])
        self.assertIsInstance(rm.current_room, KillCountRoom)
        self.assertEqual(rm.current_room.target, 25)


if __name__ == '__main__':
    unittest.main()
