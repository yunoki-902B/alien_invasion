from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class MenuButton:
    """Describe a clickable menu button."""

    label: str
    rect: pygame.Rect
    action: str
    enabled: bool = True
