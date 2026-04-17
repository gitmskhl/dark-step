import pygame
import pytmx
import os

from .utils import load_image
from . import settings


class Level:
    def __init__(self, level: int):
        self.level = level
        self.camera_x: int = 0
        self.camera_y: int = 0

        self.map = pytmx.load_pygame(os.path.join(settings.LEVEL_DIR_PATH, f"level {self.level}.tmx"))
        self.tile_size = self.map.tilewidth * settings.LEVEL_SCALE
        self._load_rigid_bodies()
        self._load_images()

    def _load_rigid_bodies(self):
        self.ridig_bodies = {}
        for (x, y, gid) in self.map.get_layer_by_name('rigid'): # type: ignore
            if gid != 0:
                self.ridig_bodies[(x, y)] = pygame.Rect(
                            x * self.tile_size,
                            y * self.tile_size,
                            self.tile_size,
                            self.tile_size
                        )
                
    def _load_images(self):
        self.background = load_image(
            os.path.join(settings.BACKGROUND_DIR_PATH, f"level {self.level}.png"),
            scale=settings.LEVEL_SCALE
        )
        
    def render(self, surface: pygame.Surface):
        surface.blit(self.background, (0 - self.camera_x, 0 - self.camera_y))
        
    def get_collision_rects(self, rect: pygame.Rect) -> list[pygame.Rect]:
        x_start = rect.left // self.tile_size
        x_end = rect.right // self.tile_size + 1
        y_start = rect.top // self.tile_size
        y_end = rect.bottom // self.tile_size + 1
        collision_rects = []
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                if (x, y) in self.ridig_bodies and rect.colliderect(self.ridig_bodies[(x, y)]):
                    collision_rects.append(self.ridig_bodies[(x, y)])
        return collision_rects

    def camera_track(self, target_x: int | float, target_y: int | float):
        self.camera_x += int((target_x - settings.SCREEN_WIDTH // 2 - self.camera_x) * settings.CAMERA_SMOOTHING)
        self.camera_y += int((target_y - settings.SCREEN_HEIGHT // 2 - self.camera_y) * settings.CAMERA_SMOOTHING)

    def get_player_coords(self) -> tuple[int, int]:
        for obj in self.map.get_layer_by_name('spawn'): # type: ignore
            return int(obj.x * settings.LEVEL_SCALE), int(obj.y * settings.LEVEL_SCALE)
        raise RuntimeError(f"No spawn point found in level {self.level}. Ensure there is an object in the 'spawn' layer of the level's TMX file.")