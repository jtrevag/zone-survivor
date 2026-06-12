import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import math
import unittest
from unittest.mock import patch
from settings import WEAPONS


def _player():
    from entities.player import Player
    return Player()


class TestPlayerEquip(unittest.TestCase):
    def test_player_starts_with_pistol(self):
        p = _player()
        self.assertEqual(p.weapon, WEAPONS['pistol'])

    def test_player_has_augments_list(self):
        p = _player()
        self.assertEqual(p.augments, [])

    def test_equip_sets_mag_size(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.mag_size, WEAPONS['shotgun']['mag_size'])

    def test_equip_sets_reload_time(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertAlmostEqual(p.reload_time, WEAPONS['shotgun']['reload_time'])

    def test_equip_sets_shot_cooldown(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertAlmostEqual(p.shot_cooldown_base, WEAPONS['shotgun']['shot_cooldown'])

    def test_equip_sets_damage(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.damage, WEAPONS['shotgun']['damage'])

    def test_equip_resets_ammo_to_mag_size(self):
        p = _player()
        p.ammo = 0
        p.equip(WEAPONS['shotgun'])
        self.assertEqual(p.ammo, WEAPONS['shotgun']['mag_size'])

    def test_equip_clears_augments(self):
        p = _player()
        p.augments = ['fake_augment']
        p.equip(WEAPONS['pistol'])
        self.assertEqual(p.augments, [])

    def test_equip_clears_reload_state(self):
        p = _player()
        p.try_reload()
        p.reload_progress = 0.5
        p.equip(WEAPONS['shotgun'])
        self.assertFalse(p.reloading)
        self.assertEqual(p.reload_progress, 0.0)

    def test_try_fire_returns_list(self):
        p = _player()
        result = p.try_fire()
        self.assertIsInstance(result, list)

    def test_pistol_fires_one_bullet(self):
        p = _player()
        bullets = p.try_fire()
        self.assertEqual(len(bullets), 1)

    def test_shotgun_fires_four_bullets(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        p.facing.update(1, 0)
        bullets = p.try_fire()
        self.assertEqual(len(bullets), 4)

    def test_shotgun_spread_is_25_degrees(self):
        p = _player()
        p.equip(WEAPONS['shotgun'])
        p.facing.update(1, 0)
        bullets = p.try_fire()
        angles = [math.degrees(math.atan2(b.vel.y, b.vel.x)) for b in bullets]
        spread = max(angles) - min(angles)
        self.assertAlmostEqual(spread, 25.0, places=3)

    def test_try_fire_empty_when_no_ammo(self):
        p = _player()
        p.ammo = 0
        self.assertEqual(p.try_fire(), [])

    def test_try_fire_empty_when_reloading(self):
        p = _player()
        p.reloading = True
        self.assertEqual(p.try_fire(), [])

    def test_try_fire_decrements_ammo(self):
        p = _player()
        before = p.ammo
        p.try_fire()
        self.assertEqual(p.ammo, before - 1)

    def test_reload_still_works_after_equip_refactor(self):
        p = _player()
        p.ammo = 0
        p.try_reload()
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(p.reload_time + 0.1)
        self.assertTrue(p.reload_complete)
        self.assertEqual(p.ammo, p.mag_size)

    def test_damage_upgrade_affects_fired_bullets(self):
        p = _player()
        p.apply_upgrade('damage')
        upgraded_damage = p.damage
        bullets = p.try_fire()
        self.assertEqual(bullets[0].damage, upgraded_damage)


if __name__ == '__main__':
    unittest.main()
