import pygame
from game.resources import resource_path


class Ship:
    """Manage the player's ship."""

    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        self.image = pygame.image.load(str(resource_path("image", "ship.png")))
        original_size = self.image.get_size()
        scaled_size = (
            max(1, int(original_size[0] * 0.7)),
            max(1, int(original_size[1] * 0.7)),
        )
        if scaled_size != original_size:
            self.image = pygame.transform.smoothscale(self.image, scaled_size)
        self.rect = self.image.get_rect()

        self.rect.midbottom = self.screen_rect.midbottom

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def update(self, dt: float = 1.0 / 60.0):
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed * dt
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed * dt
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.ship_speed * dt
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.ship_speed * dt

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def blitme(self, alpha: int | None = None):
        if alpha is None:
            self.screen.blit(self.image, self.rect)
            return

        image = self.image.copy()
        image.set_alpha(alpha)
        self.screen.blit(image, self.rect)
