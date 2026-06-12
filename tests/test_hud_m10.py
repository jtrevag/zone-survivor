import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest


def _hud():
    from ui.hud import HUD
    return HUD()


def _player():
    from entities.player import Player
    return Player()


class TestHudAugmentSquares(unittest.TestCase):
    def test_draw_with_no_augments_does_not_raise(self):
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        hud.draw(surf, p)

    def test_draw_with_two_augments_does_not_raise(self):
        from settings import AUGMENTS
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip_augment(AUGMENTS['fast_loader'])
        hud.draw(surf, p)

    def test_ammo_display_uses_effective_mag_size(self):
        from settings import AUGMENTS
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.ammo = 12
        self.assertEqual(p.effective_mag_size(), p.mag_size * 2)


if __name__ == '__main__':
    unittest.main()
