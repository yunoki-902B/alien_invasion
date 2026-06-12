import pygame
from pygame.sprite import Sprite
from game.resources import resource_path


class Alien(Sprite):
    """Represents a single alien."""
    _base_image: pygame.Surface | None = None
    _seeker_image: pygame.Surface | None = None

    def __init__(
        self,
        ai_game,
        behavior=None,
        *,
        name: str | None = None,
        max_health: int | None = None,
        move_speed_scale: float = 1.0,
        aims_player: bool = False,
        image_scale: float = 0.7,
        bullet_speed_scale: float = 1.0,
        fire_interval_scale: float = 1.0,
        bullet_damage: int | None = None,
    ):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.behavior = behavior
        self.name = name if name is not None else self.settings.alien_name
        self.is_seeker = (self.name or "").lower() == "seeker"
        self.max_health = max_health if max_health is not None else self.settings.alien_max_health
        self.current_health = self.max_health
        self.move_speed_scale = move_speed_scale
        self.aims_player = aims_player
        self.bullet_speed_scale = bullet_speed_scale
        self.fire_interval_scale = fire_interval_scale
        self.bullet_damage = bullet_damage if bullet_damage is not None else self.settings.shot_damage
        self.image_scale = max(0.2, image_scale)

        self.image = self._load_alien_image(is_seeker=self.is_seeker)
        original_size = self.image.get_size()
        scaled_size = (
            max(1, int(original_size[0] * self.image_scale)),
            max(1, int(original_size[1] * self.image_scale)),
        )
        if scaled_size != original_size:
            self.image = pygame.transform.smoothscale(self.image, scaled_size)
        self.rect = self.image.get_rect()

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.rect.x = self.rect.width
        self.rect.y = -180

        self.timer = 0.0

    @staticmethod
    def _load_base_image() -> pygame.Surface:
        return pygame.image.load(str(resource_path("image", "alien.png")))

    @classmethod
    def _load_alien_image(cls, *, is_seeker: bool = False) -> pygame.Surface:
        if cls._base_image is None:
            cls._base_image = cls._load_base_image()
            cls._seeker_image = cls._base_image.copy()
            cls._seeker_image.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if is_seeker:
            return cls._seeker_image.copy()
        return cls._base_image.copy()

    def update(self, dt: float = 1.0 / 60.0):
        if self.behavior is not None:
            self.behavior.update(self, dt)
            return

        dt = max(0.0, dt)
        self.timer += dt
        if self.y < 140:
            self.y += self.settings.alien_speed * dt
            self.rect.y = int(self.y)
        elif self.timer > 5.0:
            if self.x <= 300:
                self.x -= self.settings.alien_speed * dt
            else:
                self.x += self.settings.alien_speed * dt
            self.rect.x = int(self.x)
