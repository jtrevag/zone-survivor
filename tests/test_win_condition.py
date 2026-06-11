import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWinCondition(unittest.TestCase):
    def _make(self):
        from systems.wave_manager import WaveManager
        return WaveManager()

    def test_not_complete_at_start(self):
        wm = self._make()
        self.assertFalse(wm.is_complete)

    def test_not_complete_just_before_20_minutes(self):
        wm = self._make()
        wm.update(1199.9)
        self.assertFalse(wm.is_complete)

    def test_complete_at_20_minutes(self):
        wm = self._make()
        wm.update(1200.0)
        self.assertTrue(wm.is_complete)

    def test_complete_after_20_minutes(self):
        wm = self._make()
        wm.update(1500.0)
        self.assertTrue(wm.is_complete)


if __name__ == '__main__':
    unittest.main()
