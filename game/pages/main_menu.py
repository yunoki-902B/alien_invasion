from __future__ import annotations

import pygame

from game.pages.base import MenuButton


class MainMenu:
    """First page: Start or Quit."""

    def __init__(self, screen_size, title_font, button_font):
        self.screen_width, self.screen_height = screen_size
        self.title_font = title_font
        self.button_font = button_font
        self.selected_index = 0
        self.buttons = self._create_buttons()

    def _create_buttons(self):
        button_width = 220
        button_height = 64
        gap = 24
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        start_rect = pygame.Rect(
            center_x - button_width // 2,
            center_y - button_height // 2,
            button_width,
            button_height,
        )
        quit_rect = pygame.Rect(
            center_x - button_width // 2,
            center_y + button_height + gap - button_height // 2,
            button_width,
            button_height,
        )

        return [
            MenuButton("Start", start_rect, "start"),
            MenuButton("Quit", quit_rect, "quit"),
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "quit"
            if event.key == pygame.K_RETURN:
                return self.buttons[self.selected_index].action
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            if event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.buttons) - 1, self.selected_index + 1)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected_index = index
                    return button.action

        return None

    def draw(self, screen):
        title_surface = self.title_font.render("Alien Invasion", True, (255, 255, 255))
        title_rect = title_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 3)
        )
        screen.blit(title_surface, title_rect)

        for index, button in enumerate(self.buttons):
            rect = button.rect
            is_active = index == self.selected_index
            bg_color = (40, 120, 220) if is_active else (30, 30, 30)
            text_color = (255, 255, 255) if is_active else (220, 220, 220)

            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(screen, (200, 200, 200), rect, width=2, border_radius=8)
            text_surface = self.button_font.render(button.label, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

