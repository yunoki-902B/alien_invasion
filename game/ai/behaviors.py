"""Alien behavior strategies.

This module keeps alien movement logic isolated from entity classes so future
worlds/difficulties can change behavior by swapping strategies.
"""

from dataclasses import dataclass
from typing import Protocol
import math


class AlienBehavior(Protocol):
    """Behavior interface used by :class:`game.alien.Alien`."""

    def update(self, alien: "Alien", dt: float = 1.0 / 60.0) -> None:
        """Update alien position in-place."""


@dataclass(frozen=True)
class DescendThenSideways:
    """Current legacy movement:

    1) Move down for the first ``descent_limit`` units.
    2) After ``side_start_delay`` seconds, move left/right horizontally.
    """

    drop_speed: float
    side_speed: float
    descent_limit: float = 140.0
    side_start_delay: float = 5.0
    side_direction_switch_x: float = 300.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        alien.timer += dt
        if alien.y < self.descent_limit:
            alien.y += self.drop_speed * dt
            alien.rect.y = int(alien.y)
            return

        if alien.timer <= self.side_start_delay:
            return

        if alien.x <= self.side_direction_switch_x:
            alien.x -= self.side_speed * dt
        else:
            alien.x += self.side_speed * dt
        alien.rect.x = int(alien.x)


@dataclass(frozen=True)
class DescendThenRight:
    """Spawn from left, move down to the baseline, then drift right off-screen."""

    drop_speed: float
    side_speed: float
    descent_limit: float = 140.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        alien.timer += dt
        if alien.y < self.descent_limit:
            alien.y += self.drop_speed * dt
            alien.rect.y = int(alien.y)
            return

        alien.x += self.side_speed * dt
        alien.rect.x = int(alien.x)


@dataclass(frozen=True)
class DescendThenPauseThenRight:
    """Descend to baseline, pause, then move right off-screen."""

    drop_speed: float
    side_speed: float
    descent_limit: float = 140.0
    pause_duration: float = 2.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        phase = getattr(alien, "_pause_right_phase", 0)
        timer = getattr(alien, "_pause_right_timer", 0.0)

        if phase == 0:
            if alien.y < self.descent_limit:
                alien.y += self.drop_speed * dt
                if alien.y >= self.descent_limit:
                    alien.y = self.descent_limit
            else:
                phase = 1
                timer = 0.0
        elif phase == 1:
            timer += dt
            if timer >= self.pause_duration:
                phase = 2
                timer = 0.0
        else:
            alien.x += self.side_speed * dt

        alien._pause_right_phase = phase
        alien._pause_right_timer = timer
        alien.timer += dt
        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)


@dataclass(frozen=True)
class LeftEntryWithTwoPauses:
    """Left entry -> descend below baseline -> pause at 1/3, pause at 2/3 -> exit right."""

    drop_speed: float
    side_speed: float
    baseline_y: float = 170.0
    entry_x: float = 20.0
    first_stop_ratio: float = 1 / 3
    second_stop_ratio: float = 2 / 3
    pause_duration: float = 0.5

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        screen_width = float(alien.screen.get_width())
        if screen_width <= 0:
            return

        phase = getattr(alien, "_leftentry_phase", 0)
        timer = getattr(alien, "_leftentry_timer", 0.0)

        first_stop_x = self.first_stop_ratio * screen_width
        second_stop_x = self.second_stop_ratio * screen_width

        if phase == 0:
            if alien.x < self.entry_x:
                alien.x += self.side_speed * dt
                if alien.x > self.entry_x:
                    alien.x = self.entry_x
            elif alien.x > self.entry_x:
                alien.x -= self.side_speed * dt
                if alien.x < self.entry_x:
                    alien.x = self.entry_x
            else:
                phase = 1

        elif phase == 1:
            if alien.y < self.baseline_y:
                alien.y += self.drop_speed * dt
                if alien.y > self.baseline_y:
                    alien.y = self.baseline_y
            else:
                phase = 2

        elif phase == 2:
            if alien.x < first_stop_x:
                alien.x += self.side_speed * dt
                if alien.x > first_stop_x:
                    alien.x = first_stop_x
            else:
                phase = 3
                timer = 0.0

        elif phase == 3:
            timer += dt
            if timer >= self.pause_duration:
                phase = 4
                timer = 0.0

        elif phase == 4:
            if alien.x < second_stop_x:
                alien.x += self.side_speed * dt
                if alien.x > second_stop_x:
                    alien.x = second_stop_x
            else:
                phase = 5
                timer = 0.0

        elif phase == 5:
            timer += dt
            if timer >= self.pause_duration:
                phase = 6
                timer = 0.0

        else:
            alien.x += self.side_speed * dt

        alien.timer += dt
        alien._leftentry_phase = phase
        alien._leftentry_timer = timer
        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)


@dataclass(frozen=True)
class RightEntrySpinExitLeft:
    """Spawn from the right edge on baseline, move to center, spin, then exit left."""

    approach_speed: float
    orbit_speed: float
    orbit_radius: float = 80.0
    orbit_turns: float = 2.0
    exit_speed: float = 240.0
    baseline_y: float = 170.0
    baseline_x: float | None = None
    entry_margin: float = 20.0
    orbit_turns_speed: float | None = None
    spawn_from_right: bool = True
    orbit_tangent_to_baseline: bool = False
    orbit_tangent_below: bool = False
    orbit_start_angle: float = 0.0
    orbit_direction: float = 1.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        phase = getattr(alien, "_rtsel_phase", 0)
        angle = getattr(alien, "_rtsel_angle", 0.0)
        orbit_progress = getattr(alien, "_rtsel_orbit_progress", 0.0)
        screen_width = float(alien.screen.get_width())
        orbit_target = 2 * math.pi * float(self.orbit_turns)
        direction = 1.0 if self.orbit_direction >= 0.0 else -1.0
        orbit_speed = self.orbit_turns_speed if self.orbit_turns_speed is not None else max(
            1.0,
            self.orbit_speed,
        )

        if phase == 0:
            if self.baseline_x is None:
                target_x = float(screen_width) / 2.0
            else:
                target_x = float(self.baseline_x)

            if not hasattr(alien, "_rtsel_initialized"):
                alien.y = float(self.baseline_y)
                alien.x = max(0.0, screen_width - float(alien.rect.width) - self.entry_margin)
                setattr(alien, "_rtsel_initialized", True)

            if alien.x > target_x:
                alien.x -= self.approach_speed * dt
                if alien.x <= target_x:
                    alien.x = target_x
                    phase = 1
                    angle = float(self.orbit_start_angle)
                    orbit_progress = 0.0
            else:
                phase = 1
                angle = float(self.orbit_start_angle)
                orbit_progress = 0.0

        elif phase == 1:
            delta = orbit_speed * dt
            if direction == 0.0:
                direction = 1.0
            if orbit_target <= 0.0:
                phase = 2
                orbit_progress = 0.0
                angle = float(self.orbit_start_angle)
            else:
                angle += direction * delta
                orbit_progress += delta
                if orbit_progress >= orbit_target:
                    angle = self.orbit_start_angle + direction * orbit_target
                    orbit_progress = orbit_target
                    phase = 2

            if self.baseline_x is None:
                center_x = float(alien.screen.get_width()) / 2.0
            else:
                center_x = float(self.baseline_x)
            if self.orbit_tangent_to_baseline:
                if self.orbit_tangent_below:
                    center_y = float(self.baseline_y) + float(self.orbit_radius)
                else:
                    center_y = float(self.baseline_y) - float(self.orbit_radius)
            else:
                center_y = float(self.baseline_y)
            alien.x = center_x + self.orbit_radius * math.cos(angle)
            alien.y = center_y + self.orbit_radius * math.sin(angle)

        else:
            alien.x -= self.exit_speed * dt

        alien._rtsel_phase = phase
        alien._rtsel_angle = angle
        alien._rtsel_orbit_progress = orbit_progress
        alien.timer += dt
        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)


@dataclass(frozen=True)
class Wave6FencedDrifter:
    """Keep drift-class aliens fixed in two side groups at baseline."""

    baseline_y: float
    side: str
    index_in_side: int
    approach_speed: float
    approach_offset: float = 0.0
    side_margin: float = 20.0
    row_size: int = 3
    spacing_multiplier: float = 1.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        alien.y = float(self.baseline_y)
        phase = getattr(alien, "_w6fd_phase", 0)
        if phase == 0:
            if not hasattr(alien, "_w6fd_initialized"):
                alien.y = float(self.baseline_y)
                if self.side.lower() == "left":
                    alien.x = -float(alien.rect.width) * (1.0 + abs(self.approach_offset))
                else:
                    alien.x = float(alien.screen.get_width()) + float(alien.rect.width) * (1.0 + abs(self.approach_offset))
                setattr(alien, "_w6fd_initialized", True)

            target_x = self._target_x(alien)
            move_distance = self.approach_speed * dt
            dx = target_x - alien.x

            if abs(dx) <= move_distance:
                alien.x = target_x
                phase = 1
            else:
                direction = 1.0 if dx > 0 else -1.0
                alien.x += direction * move_distance

            if phase == 1:
                alien.x = target_x
        else:
            alien.x = self._target_x(alien)

        alien._w6fd_phase = phase
        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)

    def _target_x(self, alien) -> float:
        screen_width = float(alien.screen.get_width())
        alien_width = float(alien.rect.width)
        if alien_width <= 0:
            return float(alien.rect.x)

        row_width = (self.spacing_multiplier * (max(1, self.row_size) - 1) + 1.0) * alien_width
        step = self.spacing_multiplier * alien_width

        if self.side.lower() == "left":
            start_x = self.side_margin
        else:
            start_x = max(self.side_margin, screen_width - self.side_margin - row_width)

        start_x = max(0.0, min(start_x, max(0.0, screen_width - alien_width)))
        target_x = start_x + step * float(self.index_in_side)
        return max(0.0, min(target_x, float(alien.screen.get_width()) - alien_width))


@dataclass(frozen=True)
class Wave7SideStaticArriver:
    """Enter from one side, settle at a fixed x/y on baseline."""

    baseline_y: float
    side: str
    approach_speed: float
    side_offset_ratio: float = 0.0
    y_offset: float = 0.0
    side_margin: float = 20.0
    approach_margin_factor: float = 1.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        side = (self.side or "").lower()
        screen_width = float(alien.screen.get_width())
        if screen_width <= 0:
            return

        phase = getattr(alien, "_w7sa_phase", 0)
        if phase == 0:
            if not hasattr(alien, "_w7sa_initialized"):
                start_x = -float(alien.rect.width) * (1.0 + abs(self.approach_margin_factor))
                if side == "right":
                    start_x = float(screen_width) + float(alien.rect.width) * (1.0 + abs(self.approach_margin_factor))

                if side == "right":
                    target_x = float(screen_width) - float(alien.rect.width) - float(self.side_margin)
                else:
                    target_x = float(self.side_margin)

                target_x += float(self.side_offset_ratio) * float(alien.rect.width)
                target_y = float(self.baseline_y) + float(self.y_offset)

                screen_max_x = float(alien.screen.get_width()) - float(alien.rect.width)
                target_x = max(0.0, min(target_x, screen_max_x))

                alien.x = float(start_x)
                alien.y = float(target_y)
                alien._w7sa_target_x = target_x
                alien._w7sa_target_y = target_y
                setattr(alien, "_w7sa_initialized", True)

            target_x = float(getattr(alien, "_w7sa_target_x"))
            target_y = float(getattr(alien, "_w7sa_target_y"))
            dx = target_x - alien.x
            dy = target_y - alien.y
            distance = (dx * dx + dy * dy) ** 0.5
            move_distance = float(self.approach_speed) * dt
            if distance <= move_distance or distance == 0.0:
                alien.x = target_x
                alien.y = target_y
                phase = 1
            else:
                ratio = move_distance / distance
                alien.x += dx * ratio
                alien.y += dy * ratio

            alien._w7sa_phase = phase
        else:
            alien._w7sa_phase = phase

        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)


@dataclass(frozen=True)
class Wave7SideStaticHoldArriver:
    """Enter from one side, slide to a fixed x/y on baseline, then hold."""

    baseline_y: float
    side: str
    approach_speed: float
    y_offset: float = 0.0
    side_margin: float = 20.0
    approach_margin_factor: float = 1.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        side = (self.side or "").lower()
        screen_width = float(alien.screen.get_width())
        if screen_width <= 0:
            return

        phase = getattr(alien, "_w7sha_phase", 0)
        if phase == 0:
            if not hasattr(alien, "_w7sha_initialized"):
                start_x = -float(alien.rect.width) * (1.0 + abs(self.approach_margin_factor))
                if side == "right":
                    start_x = float(screen_width) + float(alien.rect.width) * (1.0 + abs(self.approach_margin_factor))

                if side == "right":
                    target_x = float(screen_width) - float(alien.rect.width) - float(self.side_margin)
                else:
                    target_x = float(self.side_margin)

                target_y = float(self.baseline_y) + float(self.y_offset)
                alien.x = float(start_x)
                alien.y = float(target_y)
                alien._w7sha_target_x = target_x
                alien._w7sha_target_y = target_y
                setattr(alien, "_w7sha_initialized", True)

            target_x = float(getattr(alien, "_w7sha_target_x"))
            target_y = float(getattr(alien, "_w7sha_target_y"))
            dx = target_x - alien.x
            dy = target_y - alien.y
            distance = (dx * dx + dy * dy) ** 0.5
            move_distance = float(self.approach_speed) * dt
            if distance <= move_distance or distance == 0.0:
                alien.x = target_x
                alien.y = target_y
                phase = 1
            else:
                ratio = move_distance / distance
                alien.x += dx * ratio
                alien.y += dy * ratio

            alien._w7sha_phase = phase

        else:
            alien._w7sha_phase = phase

        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)


@dataclass(frozen=True)
class Wave7BossDropAndHold:
    """Drop from above to baseline and keep standing."""

    baseline_y: float
    approach_speed: float
    boss_scale_offset: float = 0.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        phase = getattr(alien, "_w7bh_phase", 0)
        if phase == 0:
            if not hasattr(alien, "_w7bh_initialized"):
                alien.x = max(0.0, (float(alien.screen.get_width()) - float(alien.rect.width)) / 2.0)
                alien.y = -float(alien.rect.height) * (1.0 + float(self.boss_scale_offset))
                alien._w7bh_target_x = float(alien.x)
                alien._w7bh_target_y = float(self.baseline_y)
                setattr(alien, "_w7bh_initialized", True)

            target_x = float(getattr(alien, "_w7bh_target_x"))
            target_y = float(getattr(alien, "_w7bh_target_y"))
            dx = target_x - alien.x
            dy = target_y - alien.y
            distance = (dx * dx + dy * dy) ** 0.5
            move_distance = float(self.approach_speed) * dt
            if distance <= move_distance or distance == 0.0:
                alien.x = target_x
                alien.y = target_y
                phase = 1
            else:
                ratio = move_distance / distance
                alien.x += dx * ratio
                alien.y += dy * ratio

            alien._w7bh_phase = phase

        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)

@dataclass(frozen=True)
class Wave6SeekerWaver:
    """Wave 6 seeker: enters with the side drifter group and follows a sine sway."""

    approach_speed: float
    wobble_speed: float
    baseline_y: float
    side: str = "right"
    pair_index: int = 0
    hover_offset: float = -8.0
    approach_x_offset: float = 0.0
    approach_y_offset: float = -80.0
    side_margin: float = 20.0
    side_dragon_row_size: int = 3
    row_spacing_multiplier: float = 2.0
    boundary_margin: float = 14.0
    row_hide_margin: float = 6.0
    vertical_amplitude: float = 4.0
    vertical_speed: float = 6.0
    pair_spread: float = 12.0
    sine_frequency: float = 2.0
    wobble_amplitude: float = 26.0

    def update(self, alien, dt: float = 1.0 / 60.0):
        dt = max(0.0, dt)
        phase = getattr(alien, "_w6s1_phase", 0)
        timer = getattr(alien, "_w6s1_timer", 0.0)

        if phase == 0:
            if not hasattr(alien, "_w6s1_initialized"):
                start_x = -alien.rect.width
                if self.side.lower() == "right":
                    start_x = float(alien.screen.get_width()) + alien.rect.width
                alien.x = float(start_x)
                alien.y = float(self.baseline_y) + float(self.approach_y_offset)
                setattr(alien, "_w6s1_initialized", True)

            target_x, target_y = self._target_position(alien)
            dx = target_x - alien.x
            dy = target_y - alien.y
            distance = (dx * dx + dy * dy) ** 0.5
            move_distance = self.approach_speed * dt

            if distance <= move_distance or distance == 0:
                alien.x = target_x
                alien.y = target_y
                phase = 1
                timer = 0.0
            else:
                ratio = move_distance / distance
                alien.x += dx * ratio
                alien.y += dy * ratio

        else:
            left_bound, right_bound = self._compute_wobble_bounds(alien)
            center_x = 0.5 * (left_bound + right_bound)
            amplitude = min(self.wobble_amplitude, right_bound - center_x)
            phase_offset = (self.pair_index * math.pi) + float(self.approach_x_offset)
            sway_frequency = self.sine_frequency if self.sine_frequency > 0 else self.wobble_speed
            alien.x = center_x + amplitude * math.sin(timer * sway_frequency + phase_offset)
            timer += dt
            hover_y = float(self.baseline_y) + float(self.hover_offset)
            alien.y = hover_y + self.vertical_amplitude * math.sin(timer * self.vertical_speed)
        alien._w6s1_phase = phase
        alien._w6s1_timer = timer
        alien.rect.x = int(alien.x)
        alien.rect.y = int(alien.y)

    def _compute_wobble_bounds(self, alien) -> tuple[float, float]:
        screen_width = float(alien.screen.get_width())
        if screen_width <= 0:
            return 0.0, 0.0

        alien_width = float(alien.rect.width)
        row_width = (
            self.row_spacing_multiplier * (max(1, self.side_dragon_row_size) - 1) + 1.0
        ) * alien_width

        if self.side.lower() == "left":
            row_start = self.side_margin
        else:
            row_start = max(0.0, screen_width - self.side_margin - row_width)

        left_row_edge = max(row_start, self.boundary_margin)
        right_row_edge = min(
            float(alien.screen.get_width()) - alien_width - self.boundary_margin,
            row_start + row_width - alien_width - self.boundary_margin,
        )

        pair_bias = (self.pair_index - 0.5) * self.pair_spread
        pair_center = row_start + (row_width - alien_width) / 2.0 + pair_bias
        left_bound = max(left_row_edge, pair_center - row_width / 2.0 + self.row_hide_margin)
        right_bound = min(
            right_row_edge,
            pair_center + row_width / 2.0 - self.row_hide_margin,
        )

        if left_bound <= right_bound:
            return left_bound, right_bound

        center = (screen_width - alien_width) / 2.0
        return max(0.0, center - 10.0), max(0.0, min(screen_width - alien_width, center + 10.0))

    def _target_position(self, alien) -> tuple[float, float]:
        screen_width = float(alien.screen.get_width())
        if screen_width <= 0:
            return 0.0, float(self.baseline_y)

        row_width = (
            self.row_spacing_multiplier * (max(1, self.side_dragon_row_size) - 1) + 1.0
        ) * float(alien.rect.width)
        if self.side.lower() == "left":
            row_start = self.side_margin
        else:
            row_start = max(0.0, screen_width - self.side_margin - row_width)

        pair_bias = (self.pair_index - 0.5) * self.pair_spread
        target_x = row_start + (row_width - float(alien.rect.width)) / 2.0 + pair_bias
        target_x = max(0.0, min(target_x, screen_width - float(alien.rect.width)))
        target_y = float(self.baseline_y) + float(self.hover_offset)
        return target_x, target_y
