from abc import ABC, abstractmethod
from enum import Enum
import pygame
from .settings import GRAVITY
from .animation import FlippedAnimation

class EntityDirection(Enum):
    LEFT = -1
    RIGHT = 1

class Entity(ABC):
    def __init__(self, x: int, y: int, speedx: int):
        self.x = x
        self.y = y
        self.dir = EntityDirection.RIGHT
        self.speedx = speedx
        self.move_right = False
        self.move_left = False
        self.vy = 0
        self.animations: dict[str, FlippedAnimation] = {}
        self.state: str = "idle"
    
    def _update_state(self):
        if self.move_left == self.move_right:
            self.state = "idle"
        elif self.move_right:
            self.state = 'walk'
        elif self.move_left:
            self.state = 'walk'
    
    def update(self):
        if self.move_right:
            self.dir = EntityDirection.RIGHT
            self.x += self.speedx
        if self.move_left:
            self.dir = EntityDirection.LEFT
            self.x -= self.speedx
        
        self.vy += GRAVITY
        self.y += self.vy
    
        self._update_state()
        self.animations[self.state].update()
        
    def render(self, surface: pygame.Surface):
        flipped = self.dir == EntityDirection.LEFT
        self.animations[self.state].render(surface, (self.x, self.y), flipped)
    
    @abstractmethod
    def get_rect(self) -> pygame.Rect:
        pass
    