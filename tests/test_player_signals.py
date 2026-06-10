import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()


class TestPlayerHitSignals(unittest.TestCase):
    def _make(self):
        from entities.player import Player
        return Player()

    def test_hit_flash_timer_zero_at_start(self):
        p = self._make()
        self.assertEqual(p.hit_flash_timer, 0.0)

    def test_just_hit_false_at_start(self):
        p = self._make()
        self.assertFalse(p.just_hit)

    def test_reload_complete_false_at_start(self):
        p = self._make()
        self.assertFalse(p.reload_complete)

    def test_hit_flash_timer_set_on_damage(self):
        from settings import HIT_FLASH_DURATION
        p = self._make()
        p.take_damage(10)
        self.assertAlmostEqual(p.hit_flash_timer, HIT_FLASH_DURATION)

    def test_just_hit_set_on_damage(self):
        p = self._make()
        p.take_damage(10)
        self.assertTrue(p.just_hit)

    def test_no_signal_when_already_dead(self):
        p = self._make()
        p.dead = True
        p.just_hit = False
        p.take_damage(10)
        self.assertFalse(p.just_hit)

    def test_hit_flash_timer_decrements_on_update(self):
        p = self._make()
        p.take_damage(10)
        initial = p.hit_flash_timer
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(0.05)
        self.assertLess(p.hit_flash_timer, initial)
        self.assertGreater(p.hit_flash_timer, 0.0)

    def test_reload_complete_set_when_reload_finishes(self):
        p = self._make()
        p.ammo = 0
        p.try_reload()
        keys_state = [0] * 512
        with patch('pygame.key.get_pressed', return_value=keys_state), \
             patch('pygame.mouse.get_pos', return_value=(0, 0)):
            p.update(p.reload_time + 0.1)
        self.assertTrue(p.reload_complete)
        self.assertFalse(p.reloading)


if __name__ == '__main__':
    unittest.main()
