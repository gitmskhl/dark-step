import pygame

def load_image(path: str, scale: float, colorkey=None) -> pygame.Surface:
    """Load an image from the specified path, scale it, and set a colorkey if provided."""
    image = pygame.image.load(path).convert_alpha()
    if scale != 1.0:
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        image = pygame.transform.scale(image, (width, height))
    if colorkey is not None:
        image.set_colorkey(colorkey)
    
    return image


def load_images(path: str, scale: float, count: int, colorkey=None) -> list[pygame.Surface]:
    """Load a spritesheet and slice it into equal-width frames, scale them, and set a colorkey if provided."""
    spritesheet = pygame.image.load(path).convert_alpha()
    images = []
    for i in range(count):
        image = spritesheet.subsurface((i * spritesheet.get_width() // count, 0, spritesheet.get_width() // count, spritesheet.get_height()))
        if scale != 1.0:
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (width, height))
        if colorkey is not None:
            image.set_colorkey(colorkey)
        images.append(image)
    return images

