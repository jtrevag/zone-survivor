import asyncio
import pygame
import random
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES,
    HIT_FLASH_COLOR, HIT_FLASH_DURATION, HIT_FLASH_ALPHA_MAX,
    SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE,
)
from systems.sound_manager import SoundManager
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


async def main():
    pygame.mixer.pre_init(
        frequency=SOUND_SAMPLE_RATE, size=-16,
        channels=SOUND_CHANNELS, buffer=SOUND_BUFFER_SIZE,
    )
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    hud = HUD()
    sounds = SoundManager()

    _flash_surf = pygame.Surface((WIDTH, HEIGHT))
    _flash_surf.fill(HIT_FLASH_COLOR)

    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
    game_over = False
    game_won = False
    level_up = False
    pending_upgrades = []

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif game_over or game_won:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player, all_sprites, enemies, bullets, enemy_projectiles, spawner, wave_manager = new_game()
                    game_over = False
                    game_won = False
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
                        sounds.play_gunshot()

        if not game_over and not game_won and not level_up:
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

            if player.just_hit:
                sounds.play_hit()
                player.just_hit = False
            if player.reload_complete:
                sounds.play_reload()
                player.reload_complete = False

            if player.dead:
                game_over = True
                sounds.play_death()
            elif wave_manager.is_complete:
                game_won = True
            elif player.pending_level_up:
                player.pending_level_up = False
                level_up = True
                pending_upgrades = random.sample(UPGRADES, 3)

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player, wave_manager.elapsed)

        if player.hit_flash_timer > 0:
            alpha = int(HIT_FLASH_ALPHA_MAX * player.hit_flash_timer / HIT_FLASH_DURATION)
            _flash_surf.set_alpha(alpha)
            screen.blit(_flash_surf, (0, 0))

        if level_up:
            hud.draw_level_up(screen, pending_upgrades, pygame.mouse.get_pos())
        if game_over:
            hud.draw_game_over(screen, wave_manager.elapsed)
        if game_won:
            hud.draw_win_screen(screen, wave_manager.elapsed)
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
