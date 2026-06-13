import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest


class TestAugmentsSettings(unittest.TestCase):
    def test_augments_dict_exists(self):
        from settings import AUGMENTS
        self.assertIsInstance(AUGMENTS, dict)

    def test_five_augments_defined(self):
        from settings import AUGMENTS
        self.assertEqual(len(AUGMENTS), 5)

    def test_hollow_point_has_pierce_behavior(self):
        from settings import AUGMENTS
        hp = AUGMENTS['hollow_point']
        self.assertEqual(hp['pierce_count'], 1)
        self.assertAlmostEqual(hp['pierce_damage_mult'], 0.5)

    def test_drum_mag_has_mag_size_mult(self):
        from settings import AUGMENTS
        self.assertAlmostEqual(AUGMENTS['drum_mag']['mag_size_mult'], 2.0)

    def test_fast_loader_has_reload_time_mult(self):
        from settings import AUGMENTS
        self.assertAlmostEqual(AUGMENTS['fast_loader']['reload_time_mult'], 0.75)

    def test_more_pellets_has_pellet_bonus(self):
        from settings import AUGMENTS
        self.assertEqual(AUGMENTS['more_pellets']['pellet_bonus'], 2)

    def test_laser_pointer_has_no_stat_keys(self):
        from settings import AUGMENTS
        lp = AUGMENTS['laser_pointer']
        for key in ('damage_mult', 'reload_time_mult', 'mag_size_mult', 'pierce_count', 'pellet_bonus'):
            self.assertNotIn(key, lp)

    def test_all_augments_have_color(self):
        from settings import AUGMENTS
        for aid, aug in AUGMENTS.items():
            self.assertIn('color', aug, f"{aid} missing color")

    def test_all_augments_have_id_name_desc(self):
        from settings import AUGMENTS
        for aug in AUGMENTS.values():
            self.assertIn('id', aug)
            self.assertIn('name', aug)
            self.assertIn('desc', aug)

    def test_pistol_has_augments_pool(self):
        from settings import WEAPONS
        self.assertIn('augments', WEAPONS['pistol'])

    def test_shotgun_has_augments_pool(self):
        from settings import WEAPONS
        self.assertIn('augments', WEAPONS['shotgun'])

    def test_pistol_pool_has_hollow_point(self):
        from settings import WEAPONS
        self.assertIn('hollow_point', WEAPONS['pistol']['augments'])

    def test_pistol_pool_excludes_more_pellets(self):
        from settings import WEAPONS
        self.assertNotIn('more_pellets', WEAPONS['pistol']['augments'])

    def test_shotgun_pool_has_more_pellets(self):
        from settings import WEAPONS
        self.assertIn('more_pellets', WEAPONS['shotgun']['augments'])

    def test_shotgun_pool_excludes_hollow_point(self):
        from settings import WEAPONS
        self.assertNotIn('hollow_point', WEAPONS['shotgun']['augments'])

    def test_both_pools_share_laser_fast_drum(self):
        from settings import WEAPONS
        shared = {'laser_pointer', 'fast_loader', 'drum_mag'}
        self.assertTrue(shared.issubset(set(WEAPONS['pistol']['augments'])))
        self.assertTrue(shared.issubset(set(WEAPONS['shotgun']['augments'])))

    def test_all_pool_ids_exist_in_augments(self):
        from settings import WEAPONS, AUGMENTS
        for weapon in WEAPONS.values():
            for aid in weapon['augments']:
                self.assertIn(aid, AUGMENTS, f"pool references unknown augment: {aid}")


if __name__ == '__main__':
    unittest.main()
