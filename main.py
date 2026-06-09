import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR
from entities.player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    running = True
    while running:
        # Cap dt to prevent spiral-of-death on first frame and lag spikes
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        # Event pump must run before all_sprites.update() — key/mouse state depends on it
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        all_sprites.update(dt, player)

        screen.fill(BACKGROUND_COLOR)
        for entity in all_sprites:
            entity.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
