import pygame
from scripts import keybindings

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = True

    def run(self):
        while self.running:
            self.clock.tick(60)  # Limit to 60 frames per second
            self.screen.fill((0, 0, 0))  # Clear the screen with black
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == keybindings.EXIT:
                        self.running = False
                    elif event.key == keybindings.TOGGLE_FULLSCREEN:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((800, 600))  # Windowed mode
            pygame.display.flip()  # Update the display

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()