from abc import ABC, abstractmethod
from enum import Enum
import pygame
from .settings import GRAVITY
from .animation import FlippedAnimation
from .level import Level

class EntityDirection(Enum):
    LEFT = -1
    RIGHT = 1

class Entity(ABC):
    def __init__(self, x: int, y: int, speedx: int, level: Level, jump_power: int = 10, max_jumps: int = 1):
        self.x = x
        self.y = y
        self.dir = EntityDirection.RIGHT
        self.speedx = speedx
        self.jump_power = jump_power
        self.level = level
        self.move_right = False
        self.move_left = False
        self.running = False
        self.max_jumps = max_jumps
        self.jumps = 0
        self.on_ground = False
        self.vy = 0
        self.animations: dict[str, FlippedAnimation] = {}
        self._init_animations()
        self.state: str = "idle"
    
    def _update_state(self):
        if self.move_left == self.move_right:
            self.state = "idle"
        elif self.move_right:
            self.state = 'walk' if not self.running else 'run'
        elif self.move_left:
            self.state = 'walk' if not self.running else 'run'
    
    def update(self):
        if self.move_right and not self.move_left:
            self.dir = EntityDirection.RIGHT
            self.x += self.speedx * (2 if self.running else 1)
            self._collision_x(1)
        if self.move_left and not self.move_right:
            self.dir = EntityDirection.LEFT
            self.x -= self.speedx * (2 if self.running else 1)
            self._collision_x(-1)

        self.vy += GRAVITY
        self.y += self.vy
        self._collision_y()

        self._update_state()
        self.animations[self.state].update()
        
    def render(self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        flipped = self.dir == EntityDirection.LEFT
        self.animations[self.state].render(surface, (self.x - camera_x, self.y - camera_y), flipped)
        
    def jump(self):
        if self.jumps < self.max_jumps:
            self.vy = -self.jump_power
            self.jumps += 1
            self.on_ground = False
    
    def _collision_x(self, dx: int | float):
        rect = self.get_rect()
        collision_rects = self.level.get_collision_rects(rect)
        for collision_rect in collision_rects:
            if rect.colliderect(collision_rect):
                if dx > 0:
                    rect.right = collision_rect.left
                else:
                    rect.left = collision_rect.right
        self.correct_x(rect)
    
    
    def _collision_y(self):
        rect = self.get_rect()
        collision_rects = self.level.get_collision_rects(rect)
        self.on_ground = False
        for collision_rect in collision_rects:
            if rect.colliderect(collision_rect):
                if self.vy > 0:
                    rect.bottom = collision_rect.top
                    self.on_ground = True
                    self.jumps = 0
                else:
                    rect.top = collision_rect.bottom
                self.vy = 0
        self.correct_y(rect)
    
    @abstractmethod
    def get_rect(self) -> pygame.Rect:
        pass
    
    @abstractmethod
    def _init_animations(self):
        pass
    
    @abstractmethod
    def correct_x(self, rect: pygame.Rect):
        pass

    @abstractmethod
    def correct_y(self, rect: pygame.Rect):
        pass