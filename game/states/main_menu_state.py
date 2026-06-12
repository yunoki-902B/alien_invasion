"""Main menu state."""

from game.pages import MainMenu
from game.states.base import GameState, StateTransition


class MainMenuState(GameState):
    """Wrap main menu page logic into a game state."""

    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.menu = MainMenu(
            (ai_game.settings.screen_width, ai_game.settings.screen_height),
            ai_game.title_font,
            ai_game.button_font,
        )

    def start(self, payload=None):
        if payload is None:
            self.menu.selected_index = 0

    def handle_event(self, event):
        action = self.menu.handle_event(event)
        if action == "start":
            return StateTransition(next_state="level_menu")
        if action == "quit":
            return StateTransition(quit_game=True)
        return None

    def draw(self, screen):
        screen.fill(self.ai_game.settings.bg_color)
        self.menu.draw(screen)

