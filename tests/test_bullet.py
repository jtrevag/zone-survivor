import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pygame
pygame.init()
import unittest


def _make_bullet(shape='circle', radius=4, color=(255, 255, 0), speed=500, damage=55):
    from entities.projectile import Bullet
    direction = pygame.math.Vector2(1, 0)
    return Bullet((100, 100), direction, damage, radius, color, shape, speed)


class TestBullet(unittest.TestCase):
    def test_bullet_stores_radius(self):
        b = _make_bullet(radius=4)
        self.assertEqual(b.radius, 4)

    def test_bullet_stores_color(self):
        b = _make_bullet(color=(255, 0, 0))
        self.assertEqual(b.color, (255, 0, 0))

    def test_bullet_stores_shape(self):
        b = _make_bullet(shape='rect')
        self.assertEqual(b.shape, 'rect')

    def test_bullet_stores_damage(self):
        b = _make_bullet(damage=30)
        self.assertEqual(b.damage, 30)

    def test_circle_draw_does_not_raise(self):
        b = _make_bullet(shape='circle')
        surf = pygame.Surface((200, 200))
        b.draw(surf)

    def test_rect_draw_does_not_raise(self):
        b = _make_bullet(shape='rect')
        surf = pygame.Surface((200, 200))
        b.draw(surf)

    def test_bullet_rect_size_matches_radius(self):
        b = _make_bullet(radius=6)
        self.assertEqual(b.rect.width, 12)
        self.assertEqual(b.rect.height, 12)

    def test_bullet_velocity_direction(self):
        direction = pygame.math.Vector2(0, 1)
        from entities.projectile import Bullet
        b = Bullet((0, 0), direction, 55, 4, (255, 255, 0), 'circle', 300)
        self.assertAlmostEqual(b.vel.x, 0.0)
        self.assertAlmostEqual(b.vel.y, 300.0)


if __name__ == '__main__':
    unittest.main()
