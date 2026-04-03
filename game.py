import pygame
from scripts import keybindings, settings

class Game:
    def __init__(self):
        pygame.init()
        self.fullscreen = settings.DEFAULT_FULLSCREEN
        self._set_display_mode()
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)  # Limit to FPS frames per second
            self.screen.fill((0, 0, 0))  # Clear the screen with black
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == keybindings.EXIT:
                        self.running = False
                    elif event.key == keybindings.TOGGLE_FULLSCREEN:
                        self.fullscreen = not self.fullscreen
                        self._set_display_mode()
            pygame.display.flip()  # Update the display

        pygame.quit()
    
    def _set_display_mode(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))  # Windowed mode


if __name__ == "__main__":
    game = Game()
    game.run()