import pygame
import random
from settings import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES
from entities.player import Player
from entities.xp_orb import XPOrb
from systems.spawner import Spawner
from systems.wave_manager import WaveManager
from ui.hud import HUD


def new_game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    spawner = Spawner()
    wave_manager = WaveManager()
    return player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    hud = HUD()

    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
    game_over = False
    level_up = False
    pending_upgrades = []

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
                    game_over = False
            elif level_up:
                if event.type == pygame.KEYDOWN:
                    idx = event.key - pygame.K_1
                    if 0 <= idx < len(pending_upgrades):
                        player.apply_upgrade(pending_upgrades[idx]['id'])
                        level_up = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    idx = hud.hovered_upgrade(event.pos)
                    if idx >= 0:
                        player.apply_upgrade(pending_upgrades[idx]['id'])
                        level_up = False
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player.try_reload()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    bullet = player.try_fire()
                    if bullet:
                        all_sprites.add(bullet)
                        bullets.add(bullet)

        if not game_over and not level_up:
            wave_manager.update(dt)
            wp = wave_manager.params
            all_sprites.update(dt, player)
            spawner.update(dt, all_sprites, enemies, enemy_projectiles,
                           spawn_interval=wp['spawn_interval'],
                           mutant_ratio=wp['mutant_ratio'],
                           hp_mult=wp['hp_mult'])

            hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    if enemy.take_damage(bullet.damage):
                        orb = XPOrb(enemy.pos, enemy.xp_value)
                        all_sprites.add(orb)

            for proj in pygame.sprite.spritecollide(player, enemy_projectiles, True):
                player.take_damage(proj.damage)

            if player.dead:
                game_over = True
            elif player.pending_level_up:
                player.pending_level_up = False
                level_up = True
                pending_upgrades = random.sample(UPGRADES, 3)

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player, wave_manager.elapsed)
        if level_up:
            hud.draw_level_up(screen, pending_upgrades, pygame.mouse.get_pos())
        if game_over:
            hud.draw_game_over(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
