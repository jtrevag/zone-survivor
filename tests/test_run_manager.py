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


if __name__ == '__main__':
    unittest.main()
