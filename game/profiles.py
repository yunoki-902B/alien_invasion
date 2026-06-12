"""Gameplay profile registry."""

from dataclasses import dataclass
from typing import Callable

from game.ai.behaviors import DescendThenSideways


@dataclass(frozen=True)
class LevelProfile:
    """Container for gameplay configuration by world + difficulty."""

    world: int
    difficulty: int
    name: str
    behavior_builder: Callable[[float], object]
    auto_fire_interval: float = 0.1
    max_bullets: int = 3
    alien_speed_scale: float = 1.0

    def make_behavior(self, base_speed: float):
        speed = base_speed * self.alien_speed_scale
        return self.behavior_builder(speed)


WORLD_COUNT = 3
DIFFICULTY_COUNT = 5


def _world1_difficulty1():
    return LevelProfile(
        world=0,
        difficulty=0,
        name="World 1 - Difficulty 1",
        behavior_builder=lambda speed: DescendThenSideways(
            drop_speed=speed,
            side_speed=speed,
        ),
    )


def get_level_profile(world: int, difficulty: int) -> LevelProfile:
    """Return profile for the selected mode.

    Until more stages are implemented, unsupported selections route to
    World 1 - Difficulty 1 profile so runtime stays stable.
    """
    if world == 0 and difficulty == 0:
        return _world1_difficulty1()
    return _world1_difficulty1()

