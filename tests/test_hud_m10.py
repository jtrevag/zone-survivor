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


class TestDrawReward(unittest.TestCase):
    def _cards(self):
        from settings import AUGMENTS, WEAPONS
        return [
            {'type': 'weapon', 'weapon_def': WEAPONS['shotgun']},
            {'type': 'augment', 'augment_def': AUGMENTS['drum_mag']},
            {'type': 'augment', 'augment_def': AUGMENTS['fast_loader']},
        ]

    def test_draw_reward_does_not_raise(self):
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        hud.draw_reward(surf, p, self._cards(), (0, 0))

    def test_draw_reward_with_full_augments_does_not_raise(self):
        from settings import AUGMENTS
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        p.equip_augment(AUGMENTS['drum_mag'])
        p.equip_augment(AUGMENTS['fast_loader'])
        hud.draw_reward(surf, p, self._cards(), (0, 0))


class TestDrawPause(unittest.TestCase):
    def test_draw_pause_no_upgrades_does_not_raise(self):
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        hud.draw_pause(surf, p)

    def test_draw_pause_with_upgrades_and_augments_does_not_raise(self):
        from settings import AUGMENTS
        hud = _hud()
        surf = pygame.Surface((1280, 720))
        p = _player()
        p.apply_upgrade('damage')
        p.apply_upgrade('reload')
        p.apply_upgrade('damage')
        p.equip_augment(AUGMENTS['drum_mag'])
        hud.draw_pause(surf, p)


if __name__ == '__main__':
    unittest.main()
