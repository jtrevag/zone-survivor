import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR
from entities.player import Player
from systems.spawner import Spawner
from ui.hud import HUD


def new_game():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    spawner = Spawner()
    return player, all_sprites, enemies, bullets, spawner


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    hud = HUD()

    player, all_sprites, enemies, bullets, spawner = new_game()
    game_over = False

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if game_over:
                    player, all_sprites, enemies, bullets, spawner = new_game()
                    game_over = False
                else:
                    player.try_reload()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                bullet = player.try_fire()
                if bullet:
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        if not game_over:
            all_sprites.update(dt, player)
            spawner.update(dt, all_sprites, enemies)

            hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for bullet, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    enemy.take_damage(bullet.damage)

            if player.dead:
                game_over = True

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player)
        if game_over:
            hud.draw_game_over(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
