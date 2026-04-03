import pygame
from scripts import keybindings

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)  # Limit to 60 frames per second
            self.screen.fill((0, 0, 0))  # Clear the screen with black
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == keybindings.EXIT:
                        self.running = False
            pygame.display.flip()  # Update the display

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()