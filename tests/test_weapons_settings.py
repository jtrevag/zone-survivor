import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest


class TestWeaponsSettings(unittest.TestCase):
    def test_weapons_dict_exists(self):
        from settings import WEAPONS
        self.assertIsInstance(WEAPONS, dict)

    def test_pistol_exists(self):
        from settings import WEAPONS
        self.assertIn('pistol', WEAPONS)

    def test_shotgun_exists(self):
        from settings import WEAPONS
        self.assertIn('shotgun', WEAPONS)

    def test_each_weapon_has_required_keys(self):
        from settings import WEAPONS
        required = {'name', 'damage', 'mag_size', 'reload_time', 'shot_cooldown', 'pellets', 'spread', 'bullet'}
        for name, wdef in WEAPONS.items():
            with self.subTest(weapon=name):
                self.assertTrue(required.issubset(wdef.keys()))

    def test_each_bullet_def_has_required_keys(self):
        from settings import WEAPONS
        required = {'speed', 'radius', 'color', 'shape'}
        for name, wdef in WEAPONS.items():
            with self.subTest(weapon=name):
                self.assertTrue(required.issubset(wdef['bullet'].keys()))

    def test_pistol_pellets(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['pistol']['pellets'], 1)

    def test_shotgun_pellets(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['shotgun']['pellets'], 4)

    def test_shotgun_spread(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['shotgun']['spread'], 25.0)

    def test_shotgun_mag_size(self):
        from settings import WEAPONS
        self.assertEqual(WEAPONS['shotgun']['mag_size'], 2)


if __name__ == '__main__':
    unittest.main()
