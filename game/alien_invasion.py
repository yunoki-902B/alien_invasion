import sys
import time

import pygame

from game.pages import LevelMenu, MainMenu
from game.settings import Settings
from game.ship import Ship
from game.bullet import Bullet
from game.alien import Alien


class AlienInvasion:
    """Manage the overall game behavior."""

    MAIN_MENU = "main_menu"
    LEVEL_MENU = "level_menu"
    PLAYING = "playing"

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Alien Invasion")

        self.title_font = self._load_font(72)
        self.button_font = self._load_font(40)
        self.main_menu = MainMenu(
            (self.settings.screen_width, self.settings.screen_height),
            self.title_font,
            self.button_font,
        )
        self.level_menu = LevelMenu(
            (self.settings.screen_width, self.settings.screen_height),
            self.title_font,
            self.button_font,
        )

        self.state = self.MAIN_MENU
        self.selected_world = 0
        self.selected_difficulty = 0
        self.current_world = 1
        self.current_difficulty = 1
        self._reset_game_entities()

    @staticmethod
    def _load_font(size):
        """Create a font object with a safe fallback."""
        try:
            return pygame.font.SysFont(None, size)
        except Exception:
            return pygame.font.Font(None, size)

    def _reset_game_entities(self):
        self.ship = None
        self.bullets = pygame.sprite.Group()
        self.fire_pressed = False
        self.last_fire_time = 0.0
        self.aliens = pygame.sprite.Group()

    def run_game(self):
        while True:
            self._check_events()
            if self.state == self.PLAYING:
                self.ship.update()
                self._update_auto_fire()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(self.settings.clock_tick)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)

        if self.state == self.MAIN_MENU:
            self.main_menu.draw(self.screen)
            pygame.display.flip()
            return

        if self.state == self.LEVEL_MENU:
            self.level_menu.draw(self.screen)
            pygame.display.flip()
            return

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        pygame.display.flip()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
                continue

            if self.state == self.MAIN_MENU:
                self._handle_main_menu_event(event)
            elif self.state == self.LEVEL_MENU:
                self._handle_level_menu_event(event)
            else:
                self._check_play_events(event)

    def _handle_main_menu_event(self, event):
        action = self.main_menu.handle_event(event)
        if action == "start":
            self.level_menu.reset_selection()
            self.state = self.LEVEL_MENU
        elif action == "quit":
            self._quit_game()

    def _handle_level_menu_event(self, event):
        action = self.level_menu.handle_event(event)
        if action is None:
            return

        command, payload = action
        if command == "back":
            self.state = self.MAIN_MENU
        elif command == "start":
            self.selected_world = payload["world"]
            self.selected_difficulty = payload["difficulty"]
            self.current_world = self.selected_world + 1
            self.current_difficulty = self.selected_difficulty + 1
            self._start_game()

    def _start_game(self):
        self._reset_game_entities()
        self.ship = Ship(self)
        self._create_fleet()
        self.state = self.PLAYING

    def _check_play_events(self, event):
        if event.type == pygame.KEYDOWN:
            self._check_keydown_events(event)
        elif event.type == pygame.KEYUP:
            self._check_keyup_event(event)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            self._quit_game()
        elif event.key == pygame.K_SPACE:
            self.fire_pressed = True
            self._fire_bullet()
            self.last_fire_time = time.time()

    def _check_keyup_event(self, event):
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

    def _update_auto_fire(self):
        if self.fire_pressed and time.time() - self.last_fire_time >= 0.1:
            self._fire_bullet()
            self.last_fire_time = time.time()

    def _fire_bullet(self):
        if len(self.bullets) >= self.settings.max_bullets:
            return
        new_bullet = Bullet(self)
        self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

    def _create_fleet(self):
        alien = Alien(self)
        alien_width = alien.rect.width

        current_x = alien_width
        while current_x < (self.settings.screen_width - 2 * alien_width):
            new_alien = Alien(self)
            new_alien.x = current_x
            new_alien.rect.x = current_x
            self.aliens.add(new_alien)
            current_x += 2 * alien_width

    def _update_aliens(self):
        self.aliens.update()
        for alien in self.aliens.copy():
            if alien.rect.right < 0 or alien.rect.left > self.settings.screen_width:
                self.aliens.remove(alien)

    def _quit_game(self):
        pygame.quit()
        sys.exit()

