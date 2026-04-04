import pygame
from .animation import LazyFlippedAnimation
from .entity import Entity, EntityDirection
from .hitbox_config import get_profile_path, load_profile
from .settings import PLAYER_SCALE

class Player(Entity):
    def __init__(self, x: int, y: int, speedx: int):
        super().__init__(x, y, speedx)
        self._init_animations()
    
    def _init_offsets(self):
        profile_name = 'player'
        loaded = load_profile(profile_name)
        path = get_profile_path(profile_name)

        if not isinstance(loaded, dict):
            raise RuntimeError(
                f"Hitbox profile is missing or invalid: {path}. "
                "Create it with hitbox_offset_maker.py and save all required entries."
            )

        loaded_offsets = loaded.get('offsets')
        if not isinstance(loaded_offsets, dict):
            raise RuntimeError(
                f"Invalid hitbox profile format in {path}: key 'offsets' must be an object."
            )

        def ratio_for(state: str, direction: EntityDirection) -> tuple[float, float, float, float]:
            state_entry = loaded_offsets.get(state)
            if not isinstance(state_entry, dict):
                raise RuntimeError(
                    f"Missing hitbox state '{state}' in {path}. "
                    f"Expected offsets.{state}.{direction.name}."
                )

            direction_entry = state_entry.get(direction.name)
            if not isinstance(direction_entry, dict):
                raise RuntimeError(
                    f"Missing hitbox direction '{state}.{direction.name}' in {path}. "
                    "Create this entry in hitbox_offset_maker.py and press S to save."
                )

            required_keys = ('offset_x', 'offset_y', 'size_x', 'size_y')
            missing_keys = [key for key in required_keys if key not in direction_entry]
            if missing_keys:
                missing = ', '.join(missing_keys)
                raise RuntimeError(
                    f"Incomplete hitbox entry '{state}.{direction.name}' in {path}. "
                    f"Missing keys: {missing}."
                )

            try:
                return (
                    float(direction_entry['offset_x']),
                    float(direction_entry['offset_y']),
                    float(direction_entry['size_x']),
                    float(direction_entry['size_y']),
                )
            except (TypeError, ValueError) as exc:
                raise RuntimeError(
                    f"Invalid numeric values in hitbox entry '{state}.{direction.name}' in {path}. "
                    "Keys offset_x, offset_y, size_x and size_y must be numbers."
                ) from exc

        def ratios_to_pixels(size: tuple[int, int], ratios: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
            w, h = size
            return (w * ratios[0], h * ratios[1], w * ratios[2], h * ratios[3])

        idle_size = self.animations['idle'].get_current_frame().get_size()
        walk_size = self.animations['walk'].get_current_frame().get_size()
        self.hit_offsets = {
            'idle': {
                EntityDirection.RIGHT: ratios_to_pixels(idle_size, ratio_for('idle', EntityDirection.RIGHT)),
                EntityDirection.LEFT: ratios_to_pixels(idle_size, ratio_for('idle', EntityDirection.LEFT))
            },
            'walk': {
                EntityDirection.RIGHT: ratios_to_pixels(walk_size, ratio_for('walk', EntityDirection.RIGHT)),
                EntityDirection.LEFT: ratios_to_pixels(walk_size, ratio_for('walk', EntityDirection.LEFT))
            }
        }
    
    def _init_animations(self):
        self.animations = {
            'idle': LazyFlippedAnimation('images/idle.png', 10, 7, PLAYER_SCALE, repeat=True),
            'walk': LazyFlippedAnimation('images/walk.png', 10, 7, PLAYER_SCALE, repeat=True)
        }
        self._init_offsets()
    
    def render(self, surface: pygame.Surface):
        super().render(surface)
        pygame.draw.rect(surface, (255, 0, 0), self.get_rect(), 1)  # Debug: Draw hitbox
    
    def get_rect(self) -> pygame.Rect:
        offset = self.hit_offsets[self.state][self.dir]
        return pygame.Rect(self.x + offset[0], self.y + offset[1], offset[2], offset[3])