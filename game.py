import pygame
from scripts import keybindings, settings, player

class Game:
    def __init__(self):
        pygame.init()
        self.fullscreen = settings.DEFAULT_FULLSCREEN
        self._set_display_mode()
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = player.Player(100, 100, 2, 10, 1)  # Example player initialization

    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)  # Limit to FPS frames per second
            self.screen.fill((0, 0, 0))  # Clear the screen with black
            
            self.player.update()
            self.player.render(self.screen)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == keybindings.MOVE_RIGHT:
                        self.player.move_right = True
                    elif event.key == keybindings.MOVE_LEFT:
                        self.player.move_left = True
                    elif event.key == keybindings.RUN:
                        self.player.running = True
                    elif event.key == keybindings.MOVE_JUMP:
                        self.player.jump()
                    elif event.key == keybindings.EXIT:
                        self.running = False
                    elif event.key == keybindings.TOGGLE_FULLSCREEN:
                        self.fullscreen = not self.fullscreen
                        self._set_display_mode()
                elif event.type == pygame.KEYUP:
                    if event.key == keybindings.MOVE_RIGHT:
                        self.player.move_right = False
                    elif event.key == keybindings.MOVE_LEFT:
                        self.player.move_left = False
                    elif event.key == keybindings.RUN:
                        self.player.running = False
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