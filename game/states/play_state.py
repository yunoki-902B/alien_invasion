"""Main gameplay state."""

import time

import pygame

from game.alien import Alien
from game.bullet import Bullet
from game.profiles import get_level_profile
from game.ship import Ship
from game.states.base import GameState


class PlayState(GameState):
    """Core gameplay logic for world/difficulty-specific runs."""

    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.settings = ai_game.settings
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.ship = None
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.fire_pressed = False
        self.last_fire_time = 0.0
        self.profile = None
        self.auto_fire_interval = 0.1

    def start(self, payload=None):
        world = payload.get("world", 0) if payload else 0
        difficulty = payload.get("difficulty", 0) if payload else 0
        self.profile = get_level_profile(world, difficulty)
        self.auto_fire_interval = self.profile.auto_fire_interval
        self._reset_entities()
        self._create_fleet()

    def _reset_entities(self):
        self.ship = Ship(self.ai_game)
        self.bullets.empty()
        self.aliens.empty()
        self.fire_pressed = False
        self.last_fire_time = 0.0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = True
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = True
            elif event.key == pygame.K_UP:
                self.ship.moving_up = True
            elif event.key == pygame.K_DOWN:
                self.ship.moving_down = True
            elif event.key == pygame.K_q:
                return self.ai_game._request_exit()
            elif event.key == pygame.K_SPACE:
                self.fire_pressed = True
                self._fire_bullet()
                self.last_fire_time = time.time()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = False
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = False
            elif event.key == pygame.K_UP:
                self.ship.moving_up = False
            elif event.key == pygame.K_DOWN:
                self.ship.moving_down = False
            elif event.key == pygame.K_SPACE:
                self.fire_pressed = False
        return None

    def update(self):
        if self.ship is None:
            return

        self.ship.update()
        self._update_auto_fire()
        self._update_bullets()
        self._update_aliens()

    def draw(self, screen):
        screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(screen)

    def _create_fleet(self):
        alien = Alien(self.ai_game, behavior=self._make_alien_behavior())
        alien_width = alien.rect.width

        current_x = alien_width
        while current_x < (self.settings.screen_width - 2 * alien_width):
            new_alien = Alien(
                self.ai_game, behavior=self._make_alien_behavior()
            )
            new_alien.x = current_x
            new_alien.rect.x = current_x
            self.aliens.add(new_alien)
            current_x += 2 * alien_width

    def _make_alien_behavior(self):
        if self.profile is None:
            return None
        return self.profile.make_behavior(self.settings.alien_speed)

    def _update_auto_fire(self):
        if self.fire_pressed and time.time() - self.last_fire_time >= self.auto_fire_interval:
            self._fire_bullet()
            self.last_fire_time = time.time()

    def _fire_bullet(self):
        max_bullets = self.profile.max_bullets if self.profile else self.settings.max_bullets
        if len(self.bullets) >= max_bullets:
            return
        new_bullet = Bullet(self.ai_game)
        self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

    def _update_aliens(self):
        self.aliens.update()
        for alien in self.aliens.copy():
            if alien.rect.right < 0 or alien.rect.left > self.settings.screen_width:
                self.aliens.remove(alien)

