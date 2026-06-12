import pygame
from pygame.sprite import Sprite
from game.resources import resource_path


class Alien(Sprite):
    """Represents a single alien."""

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.image = pygame.image.load(str(resource_path("image", "alien.png")))
        self.rect = self.image.get_rect()

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.rect.x = self.rect.width
        self.rect.y = -180

        self.timer = 0

    def update(self):
        self.timer += 1
        if self.y < 140:
            self.y += self.settings.alien_speed
            self.rect.y = int(self.y)
        elif self.timer > 300:
            if self.x <= 300:
                self.x -= self.settings.alien_speed
            else:
                self.x += self.settings.alien_speed
            self.rect.x = int(self.x)
