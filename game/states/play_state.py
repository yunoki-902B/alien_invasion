"""Main gameplay state."""

import random
import time
import math

import pygame

from game.alien import Alien
from game.bullet import Bullet
from game.profiles import get_level_profile
from game.ship import Ship
from game.states.base import GameState, StateTransition


class PlayState(GameState):
    """Core gameplay logic for world/difficulty-specific runs."""

    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.settings = ai_game.settings
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.max_health = self.settings.player_max_health
        self.player_lives = self.settings.player_lives
        self.shot_damage = self.settings.shot_damage
        self.current_health = self.max_health
        self.current_lives = self.player_lives
        self.ship = None
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.fire_pressed = False
        self.last_fire_time = 0.0
        self.alien_fire_interval = self.settings.alien_fire_interval
        self.alien_bullet_speed = self.settings.alien_bullet_speed
        self.alien_health_scale = 1.0
        self.profile = None
        self.auto_fire_interval = 0.25
        self.invulnerable = False
        self.invulnerable_until = 0.0
        self.invulnerable_duration = 1.0
        self.blink_rate_hz = 10
        self.game_over = False
        self.level_cleared = False
        self.level = 1
        self.total_experience = 0
        self.level_exp_requirements = list(self.settings.level_exp_requirements)
        self.player_level_max = self.settings.player_level_max
        self.total_waves = 1
        self.current_wave_index = 0
        self.wave_sizes = ()
        self.wave_gaps = ()
        self.wave_alien_types = ()
        self.current_wave_alien_types = ()
        self.wave_behavior_builders = ()
        self.current_wave_behavior_builder = None
        self.wave_alien_behavior_builders = ()
        self.current_wave_alien_behavior_builders = ()
        self.wave_left_spawn = ()
        self.current_wave_left_spawn = False
        self.current_wave_id = -1
        self.wave_spawn_intervals = ()
        self.current_wave_spawn_interval = 0.0
        self.current_wave_spawn_timer = 0.0
        self.current_wave_spawn_count = 0
        self.current_wave_spawn_total = 0
        self.inter_wave_countdown = 0.0
        self.start_countdown_active = False
        self.start_countdown_seconds = 0.0
        self._start_countdown_duration = 3
        self.alien_first_shot_delay = 0.5
        self._experience_thresholds = self._build_cumulative_exp_thresholds()

    def start(self, payload=None):
        world = payload.get("world", 0) if payload else 0
        difficulty = payload.get("difficulty", 0) if payload else 0
        self.profile = get_level_profile(world, difficulty)
        self.auto_fire_interval = self.profile.auto_fire_interval
        self.max_health = self.profile.player_max_health
        self.player_lives = self.profile.player_lives
        self.shot_damage = self.profile.shot_damage
        self.alien_fire_interval = self.settings.alien_fire_interval / max(
            self.profile.alien_fire_rate_scale, 0.001
        )
        self.alien_bullet_speed = self.settings.alien_bullet_speed * self.profile.alien_bullet_speed_scale
        self.alien_health_scale = self.profile.alien_health_scale
        self.total_waves = max(1, self.profile.total_waves)
        self.wave_sizes = self.profile.wave_sizes
        self.wave_gaps = self.profile.wave_gaps
        self.wave_alien_types = self.profile.wave_alien_types
        self.wave_behavior_builders = self.profile.wave_behavior_builders
        self.wave_alien_behavior_builders = self.profile.wave_alien_behavior_builders
        self.wave_left_spawn = self.profile.wave_left_spawn
        self.wave_spawn_intervals = self.profile.wave_spawn_intervals
        self.current_health = self.max_health
        self.current_lives = self.player_lives
        self.invulnerable = False
        self.invulnerable_until = 0.0
        self.game_over = False
        self.level_cleared = False
        self.level = 1
        self.total_experience = 0
        self._reset_entities()
        self.current_wave_index = 0
        self.inter_wave_countdown = 0.0
        self.start_countdown_active = True
        self.start_countdown_seconds = float(self._start_countdown_duration)

    def _reset_entities(self):
        self.ship = Ship(self.ai_game)
        self.bullets.empty()
        self.alien_bullets.empty()
        self.aliens.empty()
        self.fire_pressed = False
        self.last_fire_time = 0.0
        self.current_wave_index = 0
        self.inter_wave_countdown = 0.0
        self.start_countdown_active = False
        self.start_countdown_seconds = 0.0
        self.current_wave_spawn_interval = 0.0
        self.current_wave_spawn_timer = 0.0
        self.current_wave_spawn_count = 0
        self.current_wave_spawn_total = 0
        self.level_cleared = False
        self.current_wave_alien_types = ()
        self.current_wave_behavior_builder = None
        self.current_wave_left_spawn = False
        self.current_wave_alien_behavior_builders = ()
        self.current_wave_id = -1

    def handle_event(self, event):
        if self.start_countdown_active:
            return None

        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return StateTransition(next_state="level_menu")
            return None

        if self.level_cleared:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return StateTransition(next_state="level_menu")
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = True
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = True
            elif event.key == pygame.K_UP:
                self.ship.moving_up = True
            elif event.key == pygame.K_DOWN:
                self.ship.moving_down = True
            elif event.key == pygame.K_SPACE:
                self.fire_pressed = True
                self._try_fire_player_bullet(force=True)
        elif event.type == pygame.KEYUP:
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
        return None

    def update(self, dt: float = 0.0):
        if self.ship is None:
            return
        if self.game_over:
            return

        if self.start_countdown_active:
            self._update_start_countdown(dt)
            return

        self._update_invulnerability()
        self.ship.update(dt)
        self._update_auto_fire()
        self._update_player_bullets(dt)
        self._update_alien_bullets(dt)
        self._update_aliens(dt)
        self._check_alien_bullet_hits()
        self._check_player_damage()
        self._update_wave_progress(dt)
        if self._check_level_complete():
            return

    def draw(self, screen):
        screen.fill(self.settings.bg_color)
        self._draw_experience_bar(screen)
        self._draw_health_bar(screen)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()
        self._draw_ship()
        self.aliens.draw(screen)
        if self.game_over:
            self._draw_game_over_overlay(screen)
        if self.level_cleared:
            self._draw_victory_overlay(screen)
        if self.start_countdown_active:
            self._draw_start_countdown_overlay(screen)

    def _update_start_countdown(self, dt: float):
        if not self.start_countdown_active:
            return

        self.start_countdown_seconds = max(0.0, self.start_countdown_seconds - dt)
        if self.start_countdown_seconds > 0:
            return

        self.start_countdown_active = False
        self._spawn_next_wave()

    def _draw_start_countdown_overlay(self, screen):
        overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        countdown_value = max(1, math.ceil(self.start_countdown_seconds))
        if countdown_value <= 0:
            countdown_value = 1

        countdown_text = self.ai_game.button_font.render(
            str(countdown_value),
            True,
            (255, 255, 255),
        )
        countdown_rect = countdown_text.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery)
        )
        screen.blit(countdown_text, countdown_rect)

    def _spawn_next_wave(self):
        if self.current_wave_index >= self.total_waves:
            return

        wave_index = self.current_wave_index
        self.current_wave_index += 1
        self.current_wave_id = wave_index
        self.current_wave_alien_types = self._resolve_wave_alien_types(wave_index)
        self.current_wave_behavior_builder = self._resolve_wave_behavior_builder(wave_index)
        self.current_wave_alien_behavior_builders = self._resolve_wave_alien_behavior_builders(wave_index)
        self.current_wave_left_spawn = self._resolve_wave_left_spawn(wave_index)
        wave_alien_count = None
        if wave_index < len(self.wave_sizes):
            wave_alien_count = self.wave_sizes[wave_index]

        if wave_alien_count is not None and wave_alien_count > 0:
            wave_spawn_interval = self._resolve_wave_spawn_interval(wave_index)
            self._create_fixed_wave(wave_alien_count, wave_spawn_interval)
            return

        self._create_default_wave()

    def _create_default_wave(self):
        alien = self._create_alien(self._alien_kind_for_wave_index(0))
        alien_width = alien.rect.width
        start_x = alien_width if not self.current_wave_left_spawn else 20
        current_x = start_x
        local_index = 0
        while current_x < (self.settings.screen_width - 2 * alien_width):
            kind = self._alien_kind_for_wave_index(local_index)
            new_alien = self._create_alien(kind, local_index)
            if self._should_force_left_entry_for_alien(kind, local_index):
                new_alien.x = -new_alien.rect.width
            else:
                new_alien.x = current_x
            new_alien.rect.x = int(new_alien.x)
            self._schedule_alien_first_shot(new_alien)
            self.aliens.add(new_alien)
            current_x += 2 * alien_width
            local_index += 1

    def _create_fixed_wave(self, alien_count: int, wave_spawn_interval: float = 0.0):
        if alien_count <= 0:
            return

        if wave_spawn_interval > 0.0:
            self._begin_wave_spawn_queue(alien_count)
            return

        alien = self._create_alien(self._alien_kind_for_wave_index(0))
        alien_width = alien.rect.width
        step_x = 2 * alien_width
        wave_width = alien_width + (alien_count - 1) * step_x
        if self.current_wave_left_spawn:
            current_x = 20
        else:
            current_x = max(0, (self.settings.screen_width - wave_width) // 2)

        for local_index in range(alien_count):
            new_alien = self._spawn_fixed_wave_alien(local_index, alien_count, current_x)
            if new_alien is None:
                continue
            current_x += step_x

    def _begin_wave_spawn_queue(self, alien_count: int):
        self.current_wave_spawn_total = max(0, alien_count)
        self.current_wave_spawn_count = 0
        self.current_wave_spawn_timer = 0.0
        self.current_wave_spawn_interval = self._resolve_wave_spawn_interval(self.current_wave_id)
        self._spawn_next_queued_alien_in_wave(alien_count)

    def _spawn_next_queued_alien_in_wave(self, alien_count: int):
        if self.current_wave_spawn_count >= self.current_wave_spawn_total:
            return

        local_index = self.current_wave_spawn_count
        new_alien = self._spawn_fixed_wave_alien(local_index, alien_count)
        if new_alien is None:
            self.current_wave_spawn_count += 1
            return

        self.current_wave_spawn_count += 1
        if self.current_wave_spawn_count < self.current_wave_spawn_total:
            self.current_wave_spawn_timer = self.current_wave_spawn_interval

    def _update_wave_spawn_queue(self, dt: float):
        if not self._is_wave_spawning():
            return

        self.current_wave_spawn_timer = max(0.0, self.current_wave_spawn_timer - dt)
        if self.current_wave_spawn_timer > 0.0:
            return

        self._spawn_next_queued_alien_in_wave(self.current_wave_spawn_total)

    def _is_wave_spawning(self):
        return self.current_wave_spawn_count < self.current_wave_spawn_total

    def _spawn_fixed_wave_alien(self, local_index: int, alien_count: int, current_x: float | None = None):
        kind = self._alien_kind_for_wave_index(local_index)
        new_alien = self._create_alien(kind, local_index)

        if self._should_force_left_entry_for_alien(kind, local_index):
            new_alien.x = -new_alien.rect.width
        elif self._spawns_from_right(new_alien):
            new_alien.x = float(self.settings.screen_width - new_alien.rect.width - 20)
            behavior_baseline_y = getattr(new_alien.behavior, "baseline_y", None)
            if behavior_baseline_y is not None:
                new_alien.y = float(behavior_baseline_y)
                new_alien.rect.y = int(new_alien.y)
        else:
            if current_x is None:
                alien_width = new_alien.rect.width
                step_x = 2 * alien_width
                wave_width = alien_width + (alien_count - 1) * step_x
                if self.current_wave_left_spawn:
                    current_x = 20
                else:
                    current_x = max(0, (self.settings.screen_width - wave_width) // 2)
            new_alien.x = float(current_x)

        new_alien.rect.x = int(new_alien.x)
        self._schedule_alien_first_shot(new_alien)
        self.aliens.add(new_alien)
        return new_alien

    def _spawns_from_right(self, alien: Alien) -> bool:
        return bool(getattr(alien.behavior, "spawn_from_right", False))

    def _schedule_alien_first_shot(self, alien: Alien):
        alien.next_fire_time = time.time() + self.alien_first_shot_delay

    def _update_wave_progress(self, dt: float):
        if self.current_wave_index >= self.total_waves:
            return

        if self._is_wave_spawning():
            self._update_wave_spawn_queue(dt)
            if self._is_wave_spawning():
                return

        if self.inter_wave_countdown > 0:
            self.inter_wave_countdown = max(0.0, self.inter_wave_countdown - dt)
            if self.inter_wave_countdown > 0:
                return
            self.inter_wave_countdown = 0.0
            self._spawn_next_wave()
            return

        if self.aliens:
            return

        next_gap = self._get_next_wave_gap()
        if next_gap > 0:
            self.inter_wave_countdown = next_gap
            return

        self._spawn_next_wave()

    def _get_next_wave_gap(self):
        gap_index = self.current_wave_index - 1
        if gap_index < 0:
            return 0.0
        if gap_index < len(self.wave_gaps):
            return float(self.wave_gaps[gap_index])
        return 0.0

    def _resolve_wave_alien_types(self, wave_index: int):
        if wave_index < len(self.wave_alien_types):
            return self.wave_alien_types[wave_index]
        return ()

    def _resolve_wave_behavior_builder(self, wave_index: int):
        if wave_index < len(self.wave_behavior_builders):
            return self.wave_behavior_builders[wave_index]
        return None

    def _resolve_wave_spawn_interval(self, wave_index: int):
        if wave_index < len(self.wave_spawn_intervals):
            return float(self.wave_spawn_intervals[wave_index])
        return 0.0

    def _resolve_wave_left_spawn(self, wave_index: int):
        if wave_index < len(self.wave_left_spawn):
            return bool(self.wave_left_spawn[wave_index])
        return False

    def _resolve_wave_alien_behavior_builders(self, wave_index: int):
        if wave_index < len(self.wave_alien_behavior_builders):
            return self.wave_alien_behavior_builders[wave_index]
        return ()

    def _alien_kind_for_wave_index(self, local_index: int):
        if not self.current_wave_alien_types:
            return "normal"

        if local_index < len(self.current_wave_alien_types):
            return self.current_wave_alien_types[local_index]

        return self.current_wave_alien_types[-1]

    def _make_alien_behavior(self, speed_scale: float = 1.0):
        if self.profile is None:
            return None
        return self.profile.make_behavior(self.settings.alien_speed * speed_scale)

    def _make_alien_behavior_for_wave(
        self,
        speed_scale: float = 1.0,
        behavior_builder=None,
    ):
        if self.profile is None:
            return None
        if behavior_builder is None:
            return self.profile.make_behavior(self.settings.alien_speed * speed_scale)

        base_speed = self.settings.alien_speed * self.profile.alien_speed_scale * speed_scale
        return behavior_builder(base_speed)

    def _resolve_alien_behavior_builder(self, local_index: int):
        if local_index < len(self.current_wave_alien_behavior_builders):
            return self.current_wave_alien_behavior_builders[local_index]
        return None

    def _should_force_left_entry_for_alien(self, kind: str, local_index: int):
        return self.current_wave_id == 2 and kind == "seeker"

    def _make_alien_health(self, base_health: int | None = None) -> int:
        base = self.settings.alien_max_health if base_health is None else base_health
        return max(1, round(base * self.alien_health_scale))

    def _create_alien(self, kind: str, local_index: int = 0):
        kind = (kind or "").lower()
        if kind == "seeker":
            speed_scale = 1.5
            health = self._make_alien_health(20)
            bullet_damage = 10
            bullet_speed_scale = 2.0
            fire_interval_scale = 2.0
            aims_player = True
            name = "Seeker"
            image_scale = 0.7
        elif kind == "boss1" or kind == "boss":
            speed_scale = 1.0
            health = self._make_alien_health(400)
            bullet_damage = self.shot_damage
            bullet_speed_scale = 1.0
            fire_interval_scale = 1.0
            aims_player = False
            name = "Boss"
            image_scale = 4.0
        else:
            speed_scale = 1.0
            health = self._make_alien_health()
            bullet_damage = self.shot_damage
            bullet_speed_scale = 1.0
            fire_interval_scale = 1.0
            aims_player = False
            name = self.settings.alien_name
            image_scale = 0.7

        alien = Alien(
            self.ai_game,
            behavior=self._make_alien_behavior_for_wave(
                speed_scale=speed_scale,
                behavior_builder=self._resolve_alien_behavior_builder(local_index)
                or self.current_wave_behavior_builder,
            ),
            name=name,
            max_health=health,
            aims_player=aims_player,
            bullet_speed_scale=bullet_speed_scale,
            fire_interval_scale=fire_interval_scale,
            bullet_damage=bullet_damage,
            move_speed_scale=speed_scale,
            image_scale=image_scale,
        )
        self._register_alien_spawn_time(alien)
        return alien

    def _register_alien_spawn_time(self, alien):
        now = time.time()
        setattr(alien, "_spawn_time", now)
        setattr(alien, "_offscreen_exit_timer", 0.0)

    def _is_entering_phase(self, alien) -> bool:
        return (
            getattr(alien, "_w6fd_phase", None) == 0
            or getattr(alien, "_w6s1_phase", None) == 0
            or getattr(alien, "_rtsel_phase", None) == 0
            or getattr(alien, "_w7sha_phase", None) == 0
            or getattr(alien, "_w7sa_phase", None) == 0
            or getattr(alien, "_w7bh_phase", None) == 0
        )

    def _update_auto_fire(self):
        if not self.fire_pressed:
            return
        self._try_fire_player_bullet()

    def _fire_bullet(self):
        if self.ship is None:
            return False

        new_bullet = Bullet(self.ai_game, start_position=self.ship.rect.midtop)
        self.bullets.add(new_bullet)
        return True

    def _try_fire_player_bullet(self, force: bool = False):
        now = time.time()
        if not force and self.last_fire_time != 0.0 and now - self.last_fire_time < self.auto_fire_interval:
            return

        if not self._fire_bullet():
            return

        self.last_fire_time = now

    def _update_player_bullets(self, dt: float):
        self.bullets.update(dt)
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            elif bullet.rect.right < 0 or bullet.rect.left > self.screen_rect.width:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _update_alien_bullets(self, dt: float):
        self.alien_bullets.update(dt)
        for bullet in self.alien_bullets.copy():
            if (
                bullet.rect.top >= self.screen_rect.bottom
                or bullet.rect.bottom <= 0
                or bullet.rect.right < 0
                or bullet.rect.left > self.screen_rect.width
            ):
                self.alien_bullets.remove(bullet)

        now = time.time()
        for alien in self.aliens.sprites():
            next_time = getattr(alien, "next_fire_time", None)
            if next_time is None:
                alien.next_fire_time = now + self.alien_first_shot_delay
                next_time = alien.next_fire_time
                if self._is_boss_alien(alien):
                    setattr(alien, "_boss_fire_cycle_start", now)

            if now >= next_time:
                self._fire_alien_bullet(alien)
                if self._is_boss_alien(alien):
                    alien.next_fire_time = now + self._get_boss_fire_interval(alien, now)
                else:
                    fire_interval = self.alien_fire_interval * getattr(alien, "fire_interval_scale", 1.0)
                    alien.next_fire_time = now + fire_interval

    def _is_boss_alien(self, alien) -> bool:
        return (alien.name or "").lower() in {"boss", "boss1"}

    def _get_alien_fire_interval(self, alien) -> float:
        return self.alien_fire_interval * getattr(alien, "fire_interval_scale", 1.0)

    def _get_boss_fire_interval(self, alien, now: float) -> float:
        if not self._is_boss_alien(alien):
            return self._get_alien_fire_interval(alien)

        cycle_start = getattr(alien, "_boss_fire_cycle_start", None)
        if cycle_start is None:
            cycle_start = now
            alien._boss_fire_cycle_start = cycle_start

        phase_time = (now - cycle_start) % 8.0
        if phase_time < 4.0:
            return 2.0 / 3.0
        return 0.5

    def _check_bullet_alien_collisions(self):
        collision_map = pygame.sprite.groupcollide(self.bullets, self.aliens, True, False)
        if not collision_map:
            return

        for player_bullet, collided_aliens in collision_map.items():
            bullet_damage = getattr(player_bullet, "damage", self.shot_damage)
            for alien in collided_aliens:
                self._damage_alien(alien, bullet_damage)

    def _check_alien_bullet_hits(self):
        if self.current_health <= 0 or self.invulnerable:
            return

        collisions = pygame.sprite.spritecollide(self.ship, self.alien_bullets, True)
        if not collisions:
            return

        damage = 0
        for bullet in collisions:
            damage += getattr(bullet, "damage", self.shot_damage)
        self._apply_damage(damage)

    def _fire_alien_bullet(self, alien):
        start_position = (alien.rect.centerx, alien.rect.bottom)
        bullet_speed = self.alien_bullet_speed * getattr(alien, "bullet_speed_scale", 1.0)
        velocity = (0, 1)
        if getattr(alien, "aims_player", False) and self.ship is not None:
            velocity = (
                float(self.ship.rect.centerx - start_position[0]),
                float(self.ship.rect.centery - start_position[1]),
            )

        if self._is_boss_alien(alien):
            phase_time = (time.time() - getattr(alien, "_boss_fire_cycle_start", time.time())) % 8.0
            if phase_time < 4.0:
                if self.ship is not None:
                    velocity = (
                        float(self.ship.rect.centerx - start_position[0]),
                        float(self.ship.rect.centery - start_position[1]),
                    )
                self._spawn_alien_bullet(
                    alien=alien,
                    start_position=start_position,
                    velocity=velocity,
                    bullet_speed=bullet_speed,
                )
            else:
                margin = max(2, int(self.settings.alien_bullet_width))
                for _ in range(2):
                    left = alien.rect.left + margin
                    right = alien.rect.right - margin
                    x = random.uniform(left, right) if right >= left else start_position[0]
                    spread_rad = random.uniform(-math.radians(30), math.radians(30))
                    velocity = (math.sin(spread_rad), math.cos(spread_rad))
                    self._spawn_alien_bullet(
                        alien=alien,
                        start_position=(x, start_position[1]),
                        velocity=velocity,
                        bullet_speed=bullet_speed,
                    )
            return

        new_bullet = self._spawn_alien_bullet(
            alien=alien,
            start_position=start_position,
            velocity=velocity,
            bullet_speed=bullet_speed,
        )
        return new_bullet

    def _spawn_alien_bullet(self, alien, start_position, velocity, bullet_speed: float):
        new_bullet = Bullet(
            self.ai_game,
            direction=1,
            start_position=start_position,
            color=self.settings.alien_bullet_color,
            speed=bullet_speed,
            velocity=velocity,
            width=self.settings.alien_bullet_width,
            height=self.settings.alien_bullet_height,
            damage=getattr(alien, "bullet_damage", self.shot_damage),
        )
        self.alien_bullets.add(new_bullet)
        return new_bullet

    def _update_aliens(self, dt: float):
        self.aliens.update(dt)
        now = time.time()
        for alien in self.aliens.copy():
            spawn_time = getattr(alien, "_spawn_time", None)
            if spawn_time is None:
                self._register_alien_spawn_time(alien)
                spawn_time = getattr(alien, "_spawn_time")

            if now - spawn_time < 1.0:
                continue

            if self._is_entering_phase(alien):
                setattr(alien, "_offscreen_exit_timer", 0.0)
                continue

            if alien.rect.right < 0 or alien.rect.left > self.settings.screen_width:
                exit_timer = float(getattr(alien, "_offscreen_exit_timer", 0.0)) + dt
                alien._offscreen_exit_timer = exit_timer
                if exit_timer >= 1.0:
                    self.aliens.remove(alien)
                continue

            alien._offscreen_exit_timer = 0.0

    def _damage_alien(self, alien, amount):
        if alien not in self.aliens:
            return

        alien.current_health -= amount
        if alien.current_health > 0:
            return

        self.aliens.remove(alien)
        self._add_experience(self.settings.alien_exp_reward)

    def _draw_ship(self):
        if not self.invulnerable:
            self.ship.blitme()
            return

        if not self._is_ship_visible():
            return

        self.ship.blitme(alpha=140)

    def _is_ship_visible(self):
        if not self.invulnerable:
            return True
        elapsed = max(self.invulnerable_until - time.time(), 0.0)
        phase = elapsed * self.blink_rate_hz
        return int(phase * 2) % 2 == 0

    def _check_player_damage(self):
        if self.current_health <= 0 or self.invulnerable:
            return

        collisions = pygame.sprite.spritecollide(self.ship, self.aliens, True)
        if not collisions:
            return

        damage = self.shot_damage * len(collisions)
        self._apply_damage(damage)

    def _apply_damage(self, amount):
        self.current_health -= amount
        if self.current_health > 0:
            return

        self.current_health = 0
        self.current_lives = max(self.current_lives - 1, 0)
        if self.current_lives <= 0:
            self.current_health = 0
            self.game_over = True
            self.fire_pressed = False
            return

        self.current_health = self.max_health
        self._start_invulnerable()

    def _add_experience(self, amount):
        if self.level >= self.player_level_max:
            return

        self.total_experience += amount
        while self.level < self.player_level_max and self.total_experience >= self._experience_thresholds[self.level]:
            self.level += 1

    def _build_cumulative_exp_thresholds(self):
        thresholds = [0]
        total = 0
        for required in self.level_exp_requirements:
            total += required
            thresholds.append(total)
        return thresholds

    def _draw_experience_bar(self, screen):
        bar_margin = 40
        bar_width = self.screen_rect.width - 2 * bar_margin
        bar_height = 16
        bar_top = 20
        bar_left = bar_margin
        background_color = (30, 45, 70)
        fill_color = (90, 220, 130)
        border_color = (220, 220, 220)

        current_exp_for_level = self._experience_thresholds[self.level - 1]
        if self.level >= self.player_level_max:
            next_level_threshold = current_exp_for_level
        else:
            next_level_threshold = self._experience_thresholds[self.level]
        exp_into_level = max(0, self.total_experience - current_exp_for_level)
        if self.level >= self.player_level_max:
            exp_progress = 1.0
            need_for_level = 1
            exp_into_level = next_level_threshold - current_exp_for_level
        else:
            need_for_level = max(1, next_level_threshold - current_exp_for_level)
            exp_progress = min(1.0, exp_into_level / need_for_level)

        background_rect = pygame.Rect(bar_left, bar_top, bar_width, bar_height)
        fill_rect = pygame.Rect(
            bar_left,
            bar_top,
            int(bar_width * exp_progress),
            bar_height,
        )

        pygame.draw.rect(screen, background_color, background_rect, border_radius=8)
        pygame.draw.rect(screen, fill_color, fill_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, background_rect, 2, border_radius=8)

        if self.level >= self.player_level_max:
            level_text = self.ai_game.button_font.render(
                f"Level {self.level} / Max",
                True,
                (255, 255, 255),
            )
        else:
            level_text = self.ai_game.button_font.render(
                f"Level {self.level}  {exp_into_level}/{need_for_level}",
                True,
                (255, 255, 255),
            )
        screen.blit(level_text, (bar_left, bar_top + 22))

    def _draw_health_bar(self, screen):
        bar_margin = 40
        bar_height = 16
        bar_top = self.screen_rect.height - 16 - bar_height
        background_color = (55, 25, 25)
        fill_color = (220, 60, 60)
        border_color = (240, 240, 240)

        max_health = max(1, self.max_health)
        health_ratio = max(0.0, min(1.0, self.current_health / max_health))

        lives_text = self.ai_game.button_font.render(
            f"life*{self.current_lives}",
            True,
            (255, 255, 255),
        )
        lives_padding = 12
        bar_left = bar_margin + lives_text.get_width() + lives_padding
        bar_width = self.screen_rect.width - bar_left - bar_margin
        lives_x = bar_margin
        lives_y = bar_top + (bar_height - lives_text.get_height()) // 2
        screen.blit(lives_text, (lives_x, lives_y))

        background_rect = pygame.Rect(bar_left, bar_top, bar_width, bar_height)
        fill_rect = pygame.Rect(
            bar_left,
            bar_top,
            int(bar_width * health_ratio),
            bar_height,
        )

        border_radius = 8
        pygame.draw.rect(screen, background_color, background_rect, border_radius=border_radius)
        pygame.draw.rect(screen, fill_color, fill_rect, border_radius=border_radius)
        pygame.draw.rect(screen, border_color, background_rect, 1, border_radius=border_radius)

    def _draw_game_over_overlay(self, screen):
        overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        game_over_text = self.ai_game.title_font.render(
            "GAME OVER",
            True,
            (255, 80, 80),
        )
        confirm_text = self.ai_game.button_font.render(
            "Press Enter to return to level select",
            True,
            (255, 255, 255),
        )

        game_over_rect = game_over_text.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery - 30)
        )
        confirm_rect = confirm_text.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery + 30)
        )

        screen.blit(game_over_text, game_over_rect)
        screen.blit(confirm_text, confirm_rect)

    def _draw_victory_overlay(self, screen):
        overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        clear_text = self.ai_game.title_font.render(
            "STAGE CLEAR",
            True,
            (110, 220, 120),
        )
        confirm_text = self.ai_game.button_font.render(
            "Press Enter to return to level select",
            True,
            (255, 255, 255),
        )

        clear_rect = clear_text.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery - 30)
        )
        confirm_rect = confirm_text.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery + 30)
        )

        screen.blit(clear_text, clear_rect)
        screen.blit(confirm_text, confirm_rect)

    def _check_level_complete(self):
        if self.current_wave_index < self.total_waves:
            return False
        if self._is_wave_spawning():
            return False
        if self.aliens:
            return False
        self.level_cleared = True
        self.fire_pressed = False
        return True

    def _start_invulnerable(self):
        self.invulnerable = True
        self.invulnerable_until = time.time() + self.invulnerable_duration

    def _update_invulnerability(self):
        if not self.invulnerable:
            return
        if time.time() >= self.invulnerable_until:
            self.invulnerable = False
            self.invulnerable_until = 0.0
