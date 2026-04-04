from abc import ABC, abstractmethod
from enum import Enum
import pygame
from .settings import GRAVITY

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
    
    def update(self):
        if self.move_left == self.move_right:
            pass
        elif self.move_right:
            self.dir = EntityDirection.RIGHT
            self.x += self.speedx
        elif self.move_left:
            self.dir = EntityDirection.LEFT
            self.x -= self.speedx
        
        self.vy += GRAVITY
        self.y += self.vy
    
    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass
    
    @abstractmethod
    def get_rect(self) -> pygame.Rect:
        pass
    
    