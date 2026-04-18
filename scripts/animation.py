import pygame

from scripts.utils import load_images

class Animation:
    def __init__(self, frames: list[pygame.Surface], frame_rate: int, repeat: bool = True):
        self.frames = frames
        self.frame_rate = frame_rate
        self.repeat = repeat
        self.current_frame = 0
        self.time_since_last_frame = 0
    
    def render(self, surface: pygame.Surface, position: tuple[float, float]) -> None:
        surface.blit(self.frames[self.current_frame], position)
    
    def update(self) -> None:
        self.time_since_last_frame += 1
        if self.time_since_last_frame >= self.frame_rate:
            self.time_since_last_frame = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.repeat:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
    
    def get_current_frame(self) -> pygame.Surface:
        return self.frames[self.current_frame]


    def reset(self) -> None:
        self.current_frame = 0
        self.time_since_last_frame = 0
    
    
class FlippedAnimation(Animation):
    def __init__(self, frames: list[pygame.Surface], frame_rate: int, repeat: bool = True):
        super().__init__(frames, frame_rate, repeat)
        self.flipped_frames = [pygame.transform.flip(frame, True, False) for frame in frames]
    
    def render(self, surface: pygame.Surface, position: tuple[float, float], flipped: bool = False) -> None:
        if flipped:
            surface.blit(self.flipped_frames[self.current_frame], position)
        else:
            surface.blit(self.frames[self.current_frame], position)
            
class LazyFlippedAnimation(FlippedAnimation):
    def __init__(self, spritesheetpath: str, frame_count: int, frame_rate: int, scale: float, colorkey=None, repeat: bool = True):
        frames = load_images(spritesheetpath, scale, frame_count, colorkey)
        super().__init__(frames, frame_rate, repeat)