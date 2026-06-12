from __future__ import annotations

import pygame

from game.pages.base import MenuButton


class LevelMenu:
    """Second page: world and difficulty selection."""

    def __init__(self, screen_size, title_font, button_font):
        self.screen_width, self.screen_height = screen_size
        self.title_font = title_font
        self.button_font = button_font

        self.worlds = ["World 1", "World 2", "World 3"]
        self.difficulties = ["1", "2", "3", "4", "5"]
        self.world_index = 0
        self.difficulty_index = 0
        self.selected_index = 0
        self.buttons = self._create_buttons()
        self.world_start = 0
        self.world_end = len(self.worlds)
        self.difficulty_start = self.world_end
        self.difficulty_end = self.difficulty_start + len(self.difficulties)
        self.confirm_index = len(self.buttons) - 1
        self._ensure_valid_selection()

    def _create_buttons(self):
        buttons = []
        world_width = 170
        world_height = 56
        diff_width = 78
        diff_height = 56
        gap = 16

        world_y = self.screen_height // 2 - 130
        world_start_x = (
            self.screen_width // 2
            - (len(self.worlds) * world_width + (len(self.worlds) - 1) * gap) // 2
        )
        self.world_y = world_y
        self.difficulty_y = world_y + 180
        for index, world in enumerate(self.worlds):
            buttons.append(
                MenuButton(
                    world,
                    pygame.Rect(
                        world_start_x + index * (world_width + gap),
                        world_y,
                        world_width,
                        world_height,
                    ),
                    f"world_{index}",
                    enabled=(index == 0),
                )
            )

        diff_start_x = (
            self.screen_width // 2
            - (len(self.difficulties) * diff_width + (len(self.difficulties) - 1) * gap) // 2
        )
        for index, difficulty in enumerate(self.difficulties):
            buttons.append(
                MenuButton(
                    difficulty,
                    pygame.Rect(
                        diff_start_x + index * (diff_width + gap),
                        self.difficulty_y,
                        diff_width,
                        diff_height,
                    ),
                    f"difficulty_{index}",
                    enabled=True,
                )
            )

        buttons.append(
            MenuButton("Start Game", pygame.Rect(self.screen_width // 2 - 90, 690, 180, 52), "confirm")
        )
        return buttons

    def _ensure_valid_selection(self):
        enabled = self._enabled_indices()
        if self.selected_index in enabled:
            return
        self.selected_index = self._first_enabled_index()

    def _enabled_indices(self):
        return [index for index, button in enumerate(self.buttons) if button.enabled]

    def _first_enabled_index(self):
        enabled = self._enabled_indices()
        return enabled[0] if enabled else self.confirm_index

    def _first_enabled_in_range(self, start: int, end: int):
        for index in range(start, end):
            if self.buttons[index].enabled:
                return index
        return None

    def _last_enabled_in_range(self, start: int, end: int):
        for index in range(end - 1, start - 1, -1):
            if self.buttons[index].enabled:
                return index
        return None

    def _button_value(self, index):
        return int(self.buttons[index].action.split("_", 1)[1])

    def _selected_button(self):
        return self.buttons[self.selected_index]

    def reset_selection(self):
        self.selected_index = 0

    def handle_event(self, event):
        """Return a tuple(command, payload) or None."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return ("back", None)

            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                selected = self._selected_button()
                if selected.action == "confirm":
                    return (
                        "start",
                        {"world": self.world_index, "difficulty": self.difficulty_index},
                    )

                if not selected.enabled:
                    return None

                if selected.action.startswith("world_"):
                    self.world_index = self._button_value(self.selected_index)
                else:
                    self.difficulty_index = self._button_value(self.selected_index)
                return None

            if event.key == pygame.K_UP:
                if self.selected_index >= self.difficulty_start:
                    target = self._last_enabled_in_range(self.world_start, self.world_end)
                    if target is None:
                        target = self.confirm_index
                    self.selected_index = target
                return None

            if event.key == pygame.K_DOWN:
                if self.selected_index < self.difficulty_start:
                    target = self._first_enabled_in_range(self.difficulty_start, self.difficulty_end)
                    if target is not None:
                        self.selected_index = target
                    else:
                        self.selected_index = self.confirm_index
                else:
                    self.selected_index = self.confirm_index
                return None

            if event.key == pygame.K_LEFT:
                if self.selected_index < self.world_end:
                    target = self.selected_index - 1
                    while target >= self.world_start:
                        if self.buttons[target].enabled:
                            self.selected_index = target
                            break
                        target -= 1
                elif self.selected_index < self.difficulty_end:
                    target = self.selected_index - 1
                    while target >= self.difficulty_start:
                        if self.buttons[target].enabled:
                            self.selected_index = target
                            break
                        target -= 1
                return None

            if event.key == pygame.K_RIGHT:
                if self.selected_index < self.world_end:
                    target = self.selected_index + 1
                    while target < self.world_end:
                        if self.buttons[target].enabled:
                            self.selected_index = target
                            break
                        target += 1
                elif self.selected_index < self.difficulty_end:
                    target = self.selected_index + 1
                    while target < self.difficulty_end:
                        if self.buttons[target].enabled:
                            self.selected_index = target
                            break
                        target += 1
                return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    if not button.enabled:
                        break
                    self.selected_index = index
                    if button.action == "confirm":
                        return (
                            "start",
                            {"world": self.world_index, "difficulty": self.difficulty_index},
                        )

                    if button.action.startswith("world_"):
                        self.world_index = self._button_value(index)
                    else:
                        self.difficulty_index = self._button_value(index)
                    return None

        return None

    def get_current_selection(self):
        return self.world_index, self.difficulty_index

    def draw(self, screen):
        title_surface = self.title_font.render(
            "Select World and Difficulty", True, (255, 255, 255)
        )
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 90))
        screen.blit(title_surface, title_rect)

        section_world = self.button_font.render("World", True, (255, 255, 255))
        section_world_rect = section_world.get_rect(midleft=(40, self.world_y - 35))
        screen.blit(section_world, section_world_rect)

        section_diff = self.button_font.render("Difficulty", True, (255, 255, 255))
        section_diff_rect = section_diff.get_rect(midleft=(40, self.difficulty_y - 35))
        screen.blit(section_diff, section_diff_rect)

        selected_world_text = self.button_font.render(
            f"Selected World: {self.worlds[self.world_index]}", True, (255, 255, 0)
        )
        selected_world_rect = selected_world_text.get_rect(midleft=(40, 560))
        screen.blit(selected_world_text, selected_world_rect)

        selected_diff_text = self.button_font.render(
            f"Selected Difficulty: {self.difficulties[self.difficulty_index]}",
            True,
            (255, 255, 0),
        )
        selected_diff_rect = selected_diff_text.get_rect(midleft=(40, 610))
        screen.blit(selected_diff_text, selected_diff_rect)

        hint_text = self.button_font.render(
            "Arrow keys select, Enter to confirm, Esc to return",
            True,
            (230, 230, 230),
        )
        hint_rect = hint_text.get_rect(midleft=(40, 665))
        screen.blit(hint_text, hint_rect)

        for index, button in enumerate(self.buttons):
            rect = button.rect
            is_active = index == self.selected_index
            if button.action == "confirm":
                is_selected = False
            elif button.action.startswith("world_"):
                is_selected = self.world_index == self._button_value(index)
            else:
                is_selected = self.difficulty_index == self._button_value(index)

            if button.enabled:
                bg_color = (40, 120, 220) if is_active else (30, 30, 30)
                if button.action == "confirm":
                    bg_color = (20, 140, 90) if is_active else (24, 100, 60)
                elif is_selected:
                    bg_color = (30, 200, 90)
                border_color = (250, 250, 250) if is_active else (200, 200, 200)
                text_color = (255, 255, 255) if is_active or is_selected else (220, 220, 220)
            else:
                bg_color = (60, 60, 60)
                text_color = (130, 130, 130)
                border_color = (85, 85, 85)

            if is_active:
                border_color = (250, 250, 250)

            if button.action == "confirm":
                border_color = (255, 255, 255) if is_active else (160, 240, 190)
                if not button.enabled:
                    border_color = (100, 170, 130)
                    text_color = (190, 230, 200)

            display_label = button.label

            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)
            text_surface = self.button_font.render(display_label, True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
