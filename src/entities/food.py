"""Food management, spawning, and special fruit countdown timers with multi-snake & obstacle support."""

import random
from typing import Sequence

from src.config import (
    FRUIT_SPECS,
    FruitType,
    GRID_COLUMNS,
    GRID_ROWS,
    SPECIAL_FRUIT_LIFESPAN_SEC,
    SPECIAL_FRUIT_SPAWN_INTERVAL,
)
from src.entities.snake import Snake


class SpecialFruit:
    """Represents a limited-time bonus fruit on the grid."""

    def __init__(self, position: list[int], fruit_type: FruitType, lifespan: float = SPECIAL_FRUIT_LIFESPAN_SEC) -> None:
        self.position: list[int] = position
        self.fruit_type: FruitType = fruit_type
        self.lifespan: float = lifespan
        self.time_remaining: float = lifespan

    @property
    def is_expired(self) -> bool:
        return self.time_remaining <= 0.0

    @property
    def progress(self) -> float:
        return max(0.0, self.time_remaining / self.lifespan)

    def update(self, dt: float) -> None:
        self.time_remaining = max(0.0, self.time_remaining - dt)


class FoodManager:
    """Manages regular and special food spawning, collision, and lifecycles."""

    def __init__(self) -> None:
        self.regular_food: list[int] = [0, 0]
        self.special_fruit: SpecialFruit | None = None
        self.regular_eaten_count: int = 0

    def reset(self, snakes: Sequence[Snake] | Snake, obstacles: set[tuple[int, int]] | None = None) -> None:
        """Resets food manager state and spawns the initial regular food."""
        self.special_fruit = None
        self.regular_eaten_count = 0
        snake_list = [snakes] if isinstance(snakes, Snake) else list(snakes)
        self.spawn_regular(snake_list, obstacles or set())

    def _get_available_cells(self, snakes: Sequence[Snake], obstacles: set[tuple[int, int]]) -> list[list[int]]:
        occupied = set(obstacles)
        for s in snakes:
            for seg in s.segments:
                occupied.add((seg[0], seg[1]))

        if self.special_fruit:
            occupied.add((self.special_fruit.position[0], self.special_fruit.position[1]))
        if self.regular_food:
            occupied.add((self.regular_food[0], self.regular_food[1]))

        available: list[list[int]] = []
        for col in range(GRID_COLUMNS):
            for row in range(GRID_ROWS):
                if (col, row) not in occupied:
                    available.append([col, row])
        return available

    def spawn_regular(self, snakes: Sequence[Snake] | Snake, obstacles: set[tuple[int, int]] | None = None) -> None:
        snake_list = [snakes] if isinstance(snakes, Snake) else list(snakes)
        available = self._get_available_cells(snake_list, obstacles or set())
        if available:
            self.regular_food = random.choice(available)

    def spawn_special(self, snakes: Sequence[Snake] | Snake, obstacles: set[tuple[int, int]] | None = None) -> None:
        snake_list = [snakes] if isinstance(snakes, Snake) else list(snakes)
        available = self._get_available_cells(snake_list, obstacles or set())
        if not available:
            return

        choice = random.choice([FruitType.GOLDEN, FruitType.FREEZE, FruitType.GHOST])
        pos = random.choice(available)
        self.special_fruit = SpecialFruit(pos, choice)

    def update(self, dt: float) -> None:
        if self.special_fruit:
            self.special_fruit.update(dt)
            if self.special_fruit.is_expired:
                self.special_fruit = None

    def on_regular_eaten(self, snakes: Sequence[Snake] | Snake, obstacles: set[tuple[int, int]] | None = None) -> None:
        snake_list = [snakes] if isinstance(snakes, Snake) else list(snakes)
        self.regular_eaten_count += 1
        self.spawn_regular(snake_list, obstacles or set())
        if self.regular_eaten_count % SPECIAL_FRUIT_SPAWN_INTERVAL == 0 and self.special_fruit is None:
            self.spawn_special(snake_list, obstacles or set())

    def check_consumption(
        self,
        head: list[int],
        snakes: Sequence[Snake] | Snake,
        obstacles: set[tuple[int, int]] | None = None,
    ) -> FruitType | None:
        snake_list = [snakes] if isinstance(snakes, Snake) else list(snakes)
        # Check special fruit first
        if self.special_fruit and head == self.special_fruit.position:
            consumed_type = self.special_fruit.fruit_type
            self.special_fruit = None
            return consumed_type

        # Check regular food
        if head == self.regular_food:
            self.on_regular_eaten(snake_list, obstacles or set())
            return FruitType.REGULAR

        return None
