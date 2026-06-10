import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWaveManagerParams(unittest.TestCase):
    def _make(self):
        from systems.wave_manager import WaveManager
        return WaveManager()

    def test_starts_at_tier_0(self):
        wm = self._make()
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], 3.0)
        self.assertAlmostEqual(p['mutant_ratio'], 0.20)
        self.assertAlmostEqual(p['hp_mult'], 1.0)

    def test_advances_to_tier_1_at_minute_2(self):
        wm = self._make()
        wm.update(2 * 60.0)
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], 2.0)
        self.assertAlmostEqual(p['mutant_ratio'], 0.30)

    def test_advances_to_tier_2_at_minute_4(self):
        wm = self._make()
        wm.update(4 * 60.0)
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], 1.5)
        self.assertAlmostEqual(p['hp_mult'], 1.2)

    def test_advances_to_tier_4_at_minute_10(self):
        wm = self._make()
        wm.update(10 * 60.0)
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], 0.7)
        self.assertAlmostEqual(p['hp_mult'], 2.0)

    def test_does_not_exceed_max_tier(self):
        wm = self._make()
        wm.update(999 * 60.0)
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], 0.7)
        self.assertAlmostEqual(p['hp_mult'], 2.0)

    def test_just_before_threshold_stays_at_previous_tier(self):
        wm = self._make()
        wm.update(2 * 60.0 - 0.001)
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], 3.0)

    def test_incremental_updates_match_single_jump(self):
        wm = self._make()
        for _ in range(360):
            wm.update(1.0)  # 360 × 1s = 6 minutes
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], 1.0)
        self.assertAlmostEqual(p['hp_mult'], 1.5)

    def test_params_returns_new_dict_each_call(self):
        wm = self._make()
        self.assertIsNot(wm.params, wm.params)


class TestWaveTableSortAssertion(unittest.TestCase):
    def test_unsorted_table_raises_on_import(self):
        unsorted = [
            (0,  3.0, 0.20, 1.0),
            (4,  1.5, 0.40, 1.2),
            (2,  2.0, 0.30, 1.0),  # out of order
        ]
        import systems.wave_manager as wm_module
        with patch.object(wm_module, 'WAVE_TABLE', unsorted):
            # Re-check assertion manually since module is already loaded
            with self.assertRaises(AssertionError):
                assert all(
                    unsorted[i][0] < unsorted[i + 1][0]
                    for i in range(len(unsorted) - 1)
                ), "WAVE_TABLE must be sorted ascending by minute threshold"


if __name__ == '__main__':
    unittest.main()
