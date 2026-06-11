import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestWaveManagerParams(unittest.TestCase):
    def test_default_params(self):
        from systems.wave_manager import WaveManager
        from settings import BASE_SPAWN_INTERVAL, BASE_HP_MULT
        wm = WaveManager()
        p = wm.params
        self.assertAlmostEqual(p['spawn_interval'], BASE_SPAWN_INTERVAL)
        self.assertAlmostEqual(p['hp_mult'], BASE_HP_MULT)
        self.assertAlmostEqual(p['mutant_ratio'], 0.4)

    def test_difficulty_scales_spawn_interval(self):
        from systems.wave_manager import WaveManager
        from settings import BASE_SPAWN_INTERVAL
        wm = WaveManager(difficulty=2.0, mutant_ratio=0.5)
        self.assertAlmostEqual(wm.params['spawn_interval'], BASE_SPAWN_INTERVAL / 2.0)

    def test_difficulty_scales_hp_mult(self):
        from systems.wave_manager import WaveManager
        from settings import BASE_HP_MULT
        wm = WaveManager(difficulty=2.0, mutant_ratio=0.5)
        self.assertAlmostEqual(wm.params['hp_mult'], BASE_HP_MULT * 2.0)

    def test_mutant_ratio_stored(self):
        from systems.wave_manager import WaveManager
        wm = WaveManager(difficulty=1.0, mutant_ratio=0.7)
        self.assertAlmostEqual(wm.params['mutant_ratio'], 0.7)

    def test_params_returns_new_dict_each_call(self):
        from systems.wave_manager import WaveManager
        wm = WaveManager()
        self.assertIsNot(wm.params, wm.params)


if __name__ == '__main__':
    unittest.main()
