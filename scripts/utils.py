import pygame
from .settings import DEBUG_MODE


def _scale_surface(image: pygame.Surface, scale: float) -> pygame.Surface:
    if scale == 1.0:
        return image
    width = int(image.get_width() * scale)
    height = int(image.get_height() * scale)
    return pygame.transform.scale(image, (width, height))


def load_image(path: str, scale: float, colorkey=None, alpha=False) -> pygame.Surface:
    """Load an image from the specified path, scale it, and set a colorkey if provided."""
    image = pygame.image.load(path)
    image = _scale_surface(image, scale)
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    if colorkey is not None:
        image.set_colorkey(colorkey)
    
    return image


def load_images(path: str, scale: float, count: int, colorkey=None) -> list[pygame.Surface]:
    """Load a spritesheet and slice it into equal-width frames, scale them, and set a colorkey if provided."""
    spritesheet = pygame.image.load(path).convert_alpha()
    images = []
    if DEBUG_MODE:
        assert spritesheet.get_width() % count == 0, f"Spritesheet width {spritesheet.get_width()} is not divisible by count {count}"
    sprite_width = spritesheet.get_width() // count
    sprite_height = spritesheet.get_height()
    for i in range(count):
        image = spritesheet.subsurface((i * sprite_width, 0, sprite_width, sprite_height))
        image = _scale_surface(image, scale)
        if colorkey is not None:
            image.set_colorkey(colorkey)
        images.append(image)
    return images

