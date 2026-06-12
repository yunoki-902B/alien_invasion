"""Gameplay profile registry."""

from dataclasses import dataclass
import math
from typing import Callable

from game.ai.behaviors import (
    RightEntrySpinExitLeft,
    DescendThenPauseThenRight,
    DescendThenSideways,
    LeftEntryWithTwoPauses,
    Wave6FencedDrifter,
    Wave6SeekerWaver,
    Wave7SideStaticArriver,
    Wave7SideStaticHoldArriver,
    Wave7BossDropAndHold,
)


@dataclass(frozen=True)
class LevelProfile:
    """Container for gameplay configuration by world + difficulty."""

    world: int
    difficulty: int
    name: str
    behavior_builder: Callable[[float], object]
    auto_fire_interval: float = 0.25
    alien_speed_scale: float = 1.0
    alien_health_scale: float = 1.0
    alien_fire_rate_scale: float = 1.0
    alien_bullet_speed_scale: float = 1.0
    player_max_health: int = 100
    player_lives: int = 3
    shot_damage: int = 20
    total_waves: int = 1
    wave_sizes: tuple[int, ...] = ()
    wave_gaps: tuple[float, ...] = ()
    wave_alien_types: tuple[tuple[str, ...], ...] = ()
    wave_spawn_intervals: tuple[float, ...] = ()
    wave_behavior_builders: tuple = ()
    wave_alien_behavior_builders: tuple = ()
    wave_left_spawn: tuple[bool, ...] = ()

    def make_behavior(self, base_speed: float):
        speed = base_speed * self.alien_speed_scale
        return self.behavior_builder(speed)


WORLD_COUNT = 3
DIFFICULTY_COUNT = 5

_WORLD1_WAVE_PATTERN = (
    ("drifter", "drifter"),
    ("drifter", "drifter", "drifter", "drifter"),
    ("drifter", "drifter", "seeker"),
    ("drifter", "drifter", "drifter", "seeker", "seeker"),
    ("seeker", "seeker", "seeker", "seeker", "seeker", "seeker", "seeker"),
    ("drifter", "drifter", "drifter", "drifter", "drifter", "drifter", "seeker"),
    ("drifter", "drifter", "seeker", "seeker", "boss1"),
)
_WORLD1_WAVE_SIZES = tuple(len(wave) for wave in _WORLD1_WAVE_PATTERN)
_WORLD1_WAVE_BEHAVIOR_BUILDERS = (
    None,
    None,
    None,
    lambda speed: DescendThenPauseThenRight(
        drop_speed=speed,
        side_speed=speed,
        pause_duration=2.0,
    ),
    None,
    None,
    None,
)
_WORLD1_WAVE_GAPS = (6.0, 6.0, 8.0, 8.0, 8.0, 8.0)
_WORLD1_WAVE_ALIEN_BEHAVIOR_BUILDERS = (
    (),
    (),
    (None, None, lambda speed: LeftEntryWithTwoPauses(drop_speed=speed, side_speed=speed)),
    (),
    (
        lambda speed: RightEntrySpinExitLeft(
            approach_speed=speed,
            orbit_speed=2 * math.pi,
            orbit_radius=160.0,
            orbit_turns=2.0,
            exit_speed=speed,
            baseline_y=170.0,
            orbit_tangent_to_baseline=True,
            orbit_tangent_below=True,
            orbit_start_angle=-math.pi / 2,
            orbit_direction=-1.0,
        ),
        lambda speed: RightEntrySpinExitLeft(
            approach_speed=speed,
            orbit_speed=2 * math.pi,
            orbit_radius=160.0,
            orbit_turns=2.0,
            exit_speed=speed,
            baseline_y=170.0,
            orbit_tangent_to_baseline=True,
            orbit_tangent_below=True,
            orbit_start_angle=-math.pi / 2,
            orbit_direction=-1.0,
        ),
        lambda speed: RightEntrySpinExitLeft(
            approach_speed=speed,
            orbit_speed=2 * math.pi,
            orbit_radius=160.0,
            orbit_turns=2.0,
            exit_speed=speed,
            baseline_y=170.0,
            orbit_tangent_to_baseline=True,
            orbit_tangent_below=True,
            orbit_start_angle=-math.pi / 2,
            orbit_direction=-1.0,
        ),
        lambda speed: RightEntrySpinExitLeft(
            approach_speed=speed,
            orbit_speed=2 * math.pi,
            orbit_radius=160.0,
            orbit_turns=2.0,
            exit_speed=speed,
            baseline_y=170.0,
            orbit_tangent_to_baseline=True,
            orbit_tangent_below=True,
            orbit_start_angle=-math.pi / 2,
            orbit_direction=-1.0,
        ),
        lambda speed: RightEntrySpinExitLeft(
            approach_speed=speed,
            orbit_speed=2 * math.pi,
            orbit_radius=160.0,
            orbit_turns=2.0,
            exit_speed=speed,
            baseline_y=170.0,
            orbit_tangent_to_baseline=True,
            orbit_tangent_below=True,
            orbit_start_angle=-math.pi / 2,
            orbit_direction=-1.0,
        ),
        lambda speed: RightEntrySpinExitLeft(
            approach_speed=speed,
            orbit_speed=2 * math.pi,
            orbit_radius=160.0,
            orbit_turns=2.0,
            exit_speed=speed,
            baseline_y=170.0,
            orbit_tangent_to_baseline=True,
            orbit_tangent_below=True,
            orbit_start_angle=-math.pi / 2,
            orbit_direction=-1.0,
        ),
        lambda speed: RightEntrySpinExitLeft(
            approach_speed=speed,
            orbit_speed=2 * math.pi,
            orbit_radius=160.0,
            orbit_turns=2.0,
            exit_speed=speed,
            baseline_y=170.0,
            orbit_tangent_to_baseline=True,
            orbit_tangent_below=True,
            orbit_start_angle=-math.pi / 2,
            orbit_direction=-1.0,
        ),
    ),
    (
        lambda speed: Wave6FencedDrifter(
            baseline_y=170.0,
            side="left",
            index_in_side=0,
            approach_speed=speed,
        ),
        lambda speed: Wave6FencedDrifter(
            baseline_y=170.0,
            side="left",
            index_in_side=1,
            approach_speed=speed,
        ),
        lambda speed: Wave6FencedDrifter(
            baseline_y=170.0,
            side="left",
            index_in_side=2,
            approach_speed=speed,
        ),
        lambda speed: Wave6FencedDrifter(
            baseline_y=170.0,
            side="right",
            index_in_side=0,
            approach_speed=speed,
        ),
        lambda speed: Wave6FencedDrifter(
            baseline_y=170.0,
            side="right",
            index_in_side=1,
            approach_speed=speed,
        ),
        lambda speed: Wave6FencedDrifter(
            baseline_y=170.0,
            side="right",
            index_in_side=2,
            approach_speed=speed,
        ),
        lambda speed: Wave6SeekerWaver(
            approach_speed=speed,
            wobble_speed=speed,
            baseline_y=170.0,
            side="right",
            approach_y_offset=-130.0,
            pair_index=1,
        ),
    ),
    (
        lambda speed: Wave7SideStaticHoldArriver(
            baseline_y=170.0,
            side="left",
            approach_speed=speed,
            approach_margin_factor=0.2,
        ),
        lambda speed: Wave7SideStaticHoldArriver(
            baseline_y=170.0,
            side="right",
            approach_speed=speed,
            approach_margin_factor=0.2,
        ),
        lambda speed: Wave7SideStaticHoldArriver(
            baseline_y=170.0,
            side="left",
            approach_speed=speed,
            y_offset=-20.0,
            approach_margin_factor=0.2,
        ),
        lambda speed: Wave7SideStaticHoldArriver(
            baseline_y=170.0,
            side="right",
            approach_speed=speed,
            y_offset=-20.0,
            approach_margin_factor=0.2,
        ),
        lambda speed: Wave7BossDropAndHold(
            baseline_y=170.0,
            approach_speed=speed,
        ),
    ),
)
_WORLD1_WAVE_LEFT_SPAWN = (False, False, False, True, False, False, False)
_WORLD1_WAVE_SPAWN_INTERVALS = (0.0, 0.0, 0.0, 0.0, 0.4, 0.0, 0.0)


def _world1_difficulty1():
    return LevelProfile(
        world=0,
        difficulty=0,
        name="World 1 - Difficulty 1",
        total_waves=7,
        wave_sizes=_WORLD1_WAVE_SIZES,
        wave_gaps=_WORLD1_WAVE_GAPS,
        wave_alien_types=_WORLD1_WAVE_PATTERN,
        wave_spawn_intervals=_WORLD1_WAVE_SPAWN_INTERVALS,
        wave_behavior_builders=_WORLD1_WAVE_BEHAVIOR_BUILDERS,
        wave_alien_behavior_builders=_WORLD1_WAVE_ALIEN_BEHAVIOR_BUILDERS,
        wave_left_spawn=_WORLD1_WAVE_LEFT_SPAWN,
        behavior_builder=lambda speed: DescendThenSideways(
            drop_speed=speed,
            side_speed=speed,
            side_start_delay=4.0,
        ),
        alien_health_scale=1.0,
        alien_fire_rate_scale=1.0,
        alien_bullet_speed_scale=1.0,
        player_max_health=100,
        player_lives=3,
        shot_damage=20,
    )


def _world1_difficulty2():
    return LevelProfile(
        world=0,
        difficulty=1,
        name="World 1 - Difficulty 2",
        total_waves=7,
        wave_sizes=_WORLD1_WAVE_SIZES,
        wave_gaps=_WORLD1_WAVE_GAPS,
        wave_alien_types=_WORLD1_WAVE_PATTERN,
        wave_spawn_intervals=_WORLD1_WAVE_SPAWN_INTERVALS,
        wave_behavior_builders=_WORLD1_WAVE_BEHAVIOR_BUILDERS,
        wave_alien_behavior_builders=_WORLD1_WAVE_ALIEN_BEHAVIOR_BUILDERS,
        wave_left_spawn=_WORLD1_WAVE_LEFT_SPAWN,
        behavior_builder=lambda speed: DescendThenSideways(
            drop_speed=speed,
            side_speed=speed,
            side_start_delay=4.0,
        ),
        alien_health_scale=1.1,
        alien_fire_rate_scale=1.0,
        alien_bullet_speed_scale=1.0,
        player_max_health=80,
        player_lives=3,
        shot_damage=20,
    )


def _world1_difficulty3():
    return LevelProfile(
        world=0,
        difficulty=2,
        name="World 1 - Difficulty 3",
        total_waves=7,
        wave_sizes=_WORLD1_WAVE_SIZES,
        wave_gaps=_WORLD1_WAVE_GAPS,
        wave_alien_types=_WORLD1_WAVE_PATTERN,
        wave_spawn_intervals=_WORLD1_WAVE_SPAWN_INTERVALS,
        wave_behavior_builders=_WORLD1_WAVE_BEHAVIOR_BUILDERS,
        wave_alien_behavior_builders=_WORLD1_WAVE_ALIEN_BEHAVIOR_BUILDERS,
        wave_left_spawn=_WORLD1_WAVE_LEFT_SPAWN,
        behavior_builder=lambda speed: DescendThenSideways(
            drop_speed=speed,
            side_speed=speed,
            side_start_delay=4.0,
        ),
        alien_health_scale=1.2,
        alien_fire_rate_scale=1.1,
        alien_bullet_speed_scale=1.2,
        player_max_health=80,
        player_lives=2,
        shot_damage=20,
    )


def _world1_difficulty4():
    return LevelProfile(
        world=0,
        difficulty=3,
        name="World 1 - Difficulty 4",
        total_waves=7,
        wave_sizes=_WORLD1_WAVE_SIZES,
        wave_gaps=_WORLD1_WAVE_GAPS,
        wave_alien_types=_WORLD1_WAVE_PATTERN,
        wave_spawn_intervals=_WORLD1_WAVE_SPAWN_INTERVALS,
        wave_behavior_builders=_WORLD1_WAVE_BEHAVIOR_BUILDERS,
        wave_alien_behavior_builders=_WORLD1_WAVE_ALIEN_BEHAVIOR_BUILDERS,
        wave_left_spawn=_WORLD1_WAVE_LEFT_SPAWN,
        behavior_builder=lambda speed: DescendThenSideways(
            drop_speed=speed,
            side_speed=speed,
            side_start_delay=4.0,
        ),
        alien_health_scale=1.3,
        alien_fire_rate_scale=1.1,
        alien_bullet_speed_scale=1.2,
        player_max_health=60,
        player_lives=2,
        shot_damage=20,
    )


def _world1_difficulty5():
    return LevelProfile(
        world=0,
        difficulty=4,
        name="World 1 - Difficulty 5",
        total_waves=7,
        wave_sizes=_WORLD1_WAVE_SIZES,
        wave_gaps=_WORLD1_WAVE_GAPS,
        wave_alien_types=_WORLD1_WAVE_PATTERN,
        wave_spawn_intervals=_WORLD1_WAVE_SPAWN_INTERVALS,
        wave_behavior_builders=_WORLD1_WAVE_BEHAVIOR_BUILDERS,
        wave_alien_behavior_builders=_WORLD1_WAVE_ALIEN_BEHAVIOR_BUILDERS,
        wave_left_spawn=_WORLD1_WAVE_LEFT_SPAWN,
        behavior_builder=lambda speed: DescendThenSideways(
            drop_speed=speed,
            side_speed=speed,
            side_start_delay=4.0,
        ),
        alien_health_scale=1.5,
        alien_fire_rate_scale=1.2,
        alien_bullet_speed_scale=1.4,
        player_max_health=60,
        player_lives=1,
        shot_damage=20,
    )


def get_level_profile(world: int, difficulty: int) -> LevelProfile:
    """Return profile for the selected mode.

    Until more stages are implemented, unsupported selections route to
    World 1 - Difficulty 1 profile so runtime stays stable.
    """
    if world == 0 and difficulty == 0:
        return _world1_difficulty1()
    if world == 0 and difficulty == 1:
        return _world1_difficulty2()
    if world == 0 and difficulty == 2:
        return _world1_difficulty3()
    if world == 0 and difficulty == 3:
        return _world1_difficulty4()
    if world == 0 and difficulty == 4:
        return _world1_difficulty5()
    return _world1_difficulty1()
