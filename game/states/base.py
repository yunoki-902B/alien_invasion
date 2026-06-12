"""State machine contracts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class StateTransition:
    """Result of one event from a state."""

    next_state: str | None = None
    payload: dict | None = None
    quit_game: bool = False


class GameState:
    """Interface all game states follow."""

    def start(self, payload: dict | None = None) -> None:
        """Called when entering the state."""

    def handle_event(self, event):
        return None

    def update(self) -> None:
        return None

    def draw(self, screen):  # pragma: no cover - delegated rendering method
        return None

