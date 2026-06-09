import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR
from entities.player import Player
from ui.hud import HUD


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    hud = HUD()

    running = True
    while running:
        # Cap dt to prevent spiral-of-death on first frame and lag spikes
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        # Event pump must run before all_sprites.update() — key/mouse state depends on it
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bullet = player.try_fire()
                if bullet:
                    all_sprites.add(bullet)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player.try_reload()

        all_sprites.update(dt, player)

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        hud.draw(screen, player)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
