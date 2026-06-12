import sys

import pygame

from game.settings import Settings
from game.states import LevelMenuState, MainMenuState, PlayState, StateTransition


class AlienInvasion:
    """Manage overall game behavior."""

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

        self.states = {
            "main_menu": MainMenuState(self),
            "level_menu": LevelMenuState(self),
            "play": PlayState(self),
        }
        self.state = self.states["main_menu"]
        self.pending_exit = False

    @staticmethod
    def _load_font(size):
        """Create a font object with a safe fallback."""
        try:
            return pygame.font.SysFont(None, size)
        except Exception:
            return pygame.font.Font(None, size)

    def run_game(self):
        while True:
            self._check_events()
            self.state.update()
            self.state.draw(self.screen)
            pygame.display.flip()
            if self.pending_exit:
                self._quit_game()
            self.clock.tick(self.settings.clock_tick)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
                continue

            transition = self.state.handle_event(event)
            self._apply_transition(transition)
            if self.pending_exit:
                return

    def _apply_transition(self, transition: StateTransition | None):
        if transition is None:
            return

        if transition.quit_game:
            self.pending_exit = True
            return

        if transition.next_state is None:
            return

        self.state = self.states[transition.next_state]
        self.state.start(transition.payload)

    def _request_exit(self):
        self.pending_exit = True

    def _quit_game(self):
        pygame.quit()
        sys.exit()

