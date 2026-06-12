import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest
from unittest.mock import patch


def _player():
    from entities.player import Player
    return Player()


class TestEquipAugment(unittest.TestCase):
    def test_equip_augment_appends_to_list(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        self.assertEqual(len(p.augments), 1)
        self.assertEqual(p.augments[0]['id'], 'drum_mag')

    def test_equip_augment_max_two(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip_augment(AUGMENTS['fast_loader'])
        p.equip_augment(AUGMENTS['laser_pointer'])  # silently ignored
        self.assertEqual(len(p.augments), 2)

    def test_augments_clear_on_weapon_swap(self):
        from settings import AUGMENTS, WEAPONS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.augments, [])


class TestEffectiveMethods(unittest.TestCase):
    def test_effective_damage_no_augments(self):
        p = _player()
        self.assertEqual(p.effective_damage(), p.damage)

    def test_effective_damage_with_damage_mult(self):
        p = _player()
        base = p.damage
        p.augments = [{'damage_mult': 1.5}]
        self.assertEqual(p.effective_damage(), int(base * 1.5))

    def test_effective_reload_time_no_augments(self):
        p = _player()
        self.assertAlmostEqual(p.effective_reload_time(), p.reload_time)

    def test_effective_reload_time_with_fast_loader(self):
        from settings import AUGMENTS
        p = _player()
        base = p.reload_time
        p.equip_augment(AUGMENTS['fast_loader'])
        self.assertAlmostEqual(p.effective_reload_time(), base * 0.75)

    def test_effective_mag_size_no_augments(self):
        p = _player()
        self.assertEqual(p.effective_mag_size(), p.mag_size)

    def test_effective_mag_size_with_drum_mag(self):
        from settings import AUGMENTS
        p = _player()
        base = p.mag_size
        p.equip_augment(AUGMENTS['drum_mag'])
        self.assertEqual(p.effective_mag_size(), int(base * 2.0))

    def test_effective_pellets_no_augments(self):
        p = _player()
        self.assertEqual(p.effective_pellets(), p.weapon['pellets'])

    def test_effective_pellets_with_more_pellets(self):
        from settings import AUGMENTS, WEAPONS
        p = _player()
        p.equip(WEAPONS['shotgun'])
        p.equip_augment(AUGMENTS['more_pellets'])
        self.assertEqual(p.effective_pellets(), 6)

    def test_effective_pierce_no_augments(self):
        p = _player()
        count, mult = p.effective_pierce()
        self.assertEqual(count, 0)

    def test_effective_pierce_with_hollow_point(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['hollow_point'])
        count, mult = p.effective_pierce()
        self.assertEqual(count, 1)
        self.assertAlmostEqual(mult, 0.5)

    def test_effective_methods_stack_multiplicatively(self):
        p = _player()
        base = p.reload_time
        p.augments = [{'reload_time_mult': 0.75}, {'reload_time_mult': 0.75}]
        self.assertAlmostEqual(p.effective_reload_time(), base * 0.75 * 0.75)


if __name__ == '__main__':
    unittest.main()
