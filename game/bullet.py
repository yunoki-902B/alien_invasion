import pygame
from pygame.sprite import Sprite

import math


class Bullet(Sprite):
    """Simple bullet used by both player and aliens."""

    def __init__(
        self,
        ai_game,
        *,
        direction: int = -1,
        start_position=None,
        color=None,
        speed: float | None = None,
        width: int | None = None,
        height: int | None = None,
        velocity: tuple[float, float] | None = None,
        damage: int | None = None,
    ):
        """Create a bullet.

        direction: -1 means upward (player), 1 means downward (alien).
        """
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.direction = direction

        self.color = color if color is not None else self.settings.bullet_color
        bullet_width = width if width is not None else self.settings.bullet_width
        bullet_height = height if height is not None else self.settings.bullet_height

        self.rect = pygame.Rect(0, 0, bullet_width, bullet_height)
        if start_position is None:
            self.rect.midtop = ai_game.ship.rect.midtop
        else:
            self.rect.centerx = int(start_position[0])
            if direction < 0:
                self.rect.bottom = int(start_position[1])
            else:
                self.rect.top = int(start_position[1])

        self.speed = speed if speed is not None else self.settings.bullet_speed
        self.y = float(self.rect.y)
        self.x = float(self.rect.x)
        self.damage = damage if damage is not None else self.settings.shot_damage
        self.vx = 0.0
        self.vy = float(self.direction)

        if velocity is not None:
            vx, vy = map(float, velocity)
            vector_mag = math.hypot(vx, vy)
            if vector_mag > 0:
                scale = self.speed / vector_mag
                self.vx = vx * scale
                self.vy = vy * scale
            else:
                self.vy = self.speed * self.direction
                self.vx = 0.0
        else:
            self.vy = self.speed * self.direction
            self.vx = 0.0

    def update(self, dt: float = 1.0 / 60.0):
        # speed is pixels per second; dt is elapsed seconds.
        dt = max(0.0, dt)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
