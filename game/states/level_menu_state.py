"""World and difficulty selection state."""

from game.pages import LevelMenu
from game.states.base import GameState, StateTransition


class LevelMenuState(GameState):
    """Wrap level/world selection page into state flow."""

    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.menu = LevelMenu(
            (ai_game.settings.screen_width, ai_game.settings.screen_height),
            ai_game.title_font,
            ai_game.button_font,
        )

    def start(self, payload=None):
        self.menu.reset_selection()

    def handle_event(self, event):
        action = self.menu.handle_event(event)
        if action is None:
            return None

        command, payload = action
        if command == "back":
            return StateTransition(next_state="main_menu")
        if command == "start":
            return StateTransition(
                next_state="play",
                payload={
                    "world": payload["world"],
                    "difficulty": payload["difficulty"],
                },
            )
        return None

    def draw(self, screen):
        screen.fill(self.ai_game.settings.bg_color)
        self.menu.draw(screen)

