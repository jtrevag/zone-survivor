import asyncio
import pygame
import random
from settings import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, UPGRADES,
    HIT_FLASH_COLOR, HIT_FLASH_DURATION, HIT_FLASH_ALPHA_MAX,
    SOUND_SAMPLE_RATE, SOUND_CHANNELS, SOUND_BUFFER_SIZE,
    ROOM_SEQUENCE, WEAPONS,
)
from systems.sound_manager import SoundManager
from entities.player import Player
from entities.xp_orb import XPOrb
from systems.spawner import Spawner
from systems.run_manager import RunManager
from ui.hud import HUD


def new_game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    xp_orbs = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    spawner = Spawner()
    run_manager = RunManager(ROOM_SEQUENCE)
    return player, all_sprites, enemies, bullets, enemy_projectiles, xp_orbs, spawner, run_manager


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

    player, all_sprites, enemies, bullets, enemy_projectiles, xp_orbs, spawner, run_manager = new_game()
    level_up = False
    pending_upgrades = []

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif run_manager.state in ('WIN', 'GAME_OVER'):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    player, all_sprites, enemies, bullets, enemy_projectiles, xp_orbs, spawner, run_manager = new_game()
                    level_up = False
                    pending_upgrades = []
            elif run_manager.state == 'REWARD':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    for e in list(enemies):
                        e.kill()
                    for p in list(enemy_projectiles):
                        p.kill()
                    for o in list(xp_orbs):
                        o.kill()
                    run_manager.advance()
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
                    fired = player.try_fire()
                    if fired:
                        for bullet in fired:
                            all_sprites.add(bullet)
                            bullets.add(bullet)
                        sounds.play_gunshot()
                # DEV ONLY — remove in M10 when reward screen handles weapon equip
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                    if player.weapon is WEAPONS['pistol']:
                        player.equip(WEAPONS['shotgun'])
                    else:
                        player.equip(WEAPONS['pistol'])
                    print(f"[DEV] weapon: {player.weapon['name']}")

        if run_manager.state == 'ENCOUNTER' and not level_up:
            run_manager.update(dt)
            all_sprites.update(dt, player)
            if run_manager.current_room.spawns_waves:
                wp = run_manager.wave_manager.params
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
                        xp_orbs.add(orb)
                        run_manager.record_kill()

            for proj in pygame.sprite.spritecollide(player, enemy_projectiles, True):
                player.take_damage(proj.damage)

            if player.just_hit:
                sounds.play_hit()
                player.just_hit = False
            if player.reload_complete:
                sounds.play_reload()
                player.reload_complete = False

            if player.dead:
                run_manager.on_player_death()
                sounds.play_death()
            elif player.pending_level_up:
                player.pending_level_up = False
                level_up = True
                pending_upgrades = random.sample(UPGRADES, 3)

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player, run_manager.current_room)

        if player.hit_flash_timer > 0:
            player.hit_flash_timer = max(0.0, player.hit_flash_timer - dt)
            alpha = int(HIT_FLASH_ALPHA_MAX * player.hit_flash_timer / HIT_FLASH_DURATION)
            _flash_surf.set_alpha(alpha)
            screen.blit(_flash_surf, (0, 0))

        if level_up:
            hud.draw_level_up(screen, pending_upgrades, pygame.mouse.get_pos())
        if run_manager.state == 'REWARD':
            hud.draw_room_clear(screen)
        if run_manager.state == 'GAME_OVER':
            hud.draw_game_over(screen, run_manager.run_elapsed)
        if run_manager.state == 'WIN':
            hud.draw_win_screen(screen, run_manager.run_elapsed)
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


# Pygbag (WASM) requires asyncio.run at module level — do not add an __name__ guard.
asyncio.run(main())
