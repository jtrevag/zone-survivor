import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest


def _bullet(pierce_count=0, pierce_damage_mult=0.5, damage=100):
    from entities.projectile import Bullet
    return Bullet(
        (100, 100), pygame.math.Vector2(1, 0), damage,
        4, (255, 255, 0), 'circle', 500,
        pierce_count=pierce_count, pierce_damage_mult=pierce_damage_mult,
    )


class MockEnemy:
    def __init__(self):
        self.damage_received = []
    def take_damage(self, amount):
        self.damage_received.append(amount)
        return False


class TestBulletPierce(unittest.TestCase):
    def test_default_pierce_count_is_zero(self):
        from entities.projectile import Bullet
        b = Bullet((0, 0), pygame.math.Vector2(1, 0), 55, 4, (255, 255, 0), 'circle', 500)
        self.assertEqual(b.pierce_count, 0)

    def test_pierce_count_stored(self):
        b = _bullet(pierce_count=1)
        self.assertEqual(b.pierce_count, 1)

    def test_on_hit_no_pierce_returns_true(self):
        b = _bullet(pierce_count=0)
        result = b.on_hit(MockEnemy())
        self.assertTrue(result)

    def test_on_hit_no_pierce_deals_full_damage(self):
        b = _bullet(pierce_count=0, damage=55)
        e = MockEnemy()
        b.on_hit(e)
        self.assertEqual(e.damage_received, [55])

    def test_on_hit_pierce_returns_false(self):
        b = _bullet(pierce_count=1)
        result = b.on_hit(MockEnemy())
        self.assertFalse(result)

    def test_on_hit_pierce_deals_full_damage_to_first_enemy(self):
        b = _bullet(pierce_count=1, damage=100)
        e = MockEnemy()
        b.on_hit(e)
        self.assertEqual(e.damage_received, [100])

    def test_on_hit_pierce_halves_damage(self):
        b = _bullet(pierce_count=1, pierce_damage_mult=0.5, damage=100)
        b.on_hit(MockEnemy())
        self.assertEqual(b.damage, 50)

    def test_on_hit_pierce_decrements_count(self):
        b = _bullet(pierce_count=1)
        b.on_hit(MockEnemy())
        self.assertEqual(b.pierce_count, 0)

    def test_on_hit_second_hit_returns_true(self):
        b = _bullet(pierce_count=1)
        b.on_hit(MockEnemy())   # pierces first
        result = b.on_hit(MockEnemy())
        self.assertTrue(result)

    def test_on_hit_second_hit_deals_halved_damage(self):
        b = _bullet(pierce_count=1, pierce_damage_mult=0.5, damage=100)
        b.on_hit(MockEnemy())   # pierces: damage → 50
        e2 = MockEnemy()
        b.on_hit(e2)
        self.assertEqual(e2.damage_received, [50])


if __name__ == '__main__':
    unittest.main()
