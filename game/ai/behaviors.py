"""Alien behavior strategies.

This module keeps alien movement logic isolated from entity classes so future
worlds/difficulties can change behavior by swapping strategies.
"""

from dataclasses import dataclass
from typing import Protocol


class AlienBehavior(Protocol):
    """Behavior interface used by :class:`game.alien.Alien`."""

    def update(self, alien: "Alien") -> None:
        """Update alien position in-place."""


@dataclass(frozen=True)
class DescendThenSideways:
    """Current legacy movement:

    1) Move down for the first ``descent_limit`` units.
    2) After ``side_start_frame`` frames, move left/right horizontally.
    """

    drop_speed: float
    side_speed: float
    descent_limit: float = 140.0
    side_start_frame: int = 300
    side_direction_switch_x: float = 300.0

    def update(self, alien):
        alien.timer += 1
        if alien.y < self.descent_limit:
            alien.y += self.drop_speed
            alien.rect.y = int(alien.y)
            return

        if alien.timer <= self.side_start_frame:
            return

        if alien.x <= self.side_direction_switch_x:
            alien.x -= self.side_speed
        else:
            alien.x += self.side_speed
        alien.rect.x = int(alien.x)

