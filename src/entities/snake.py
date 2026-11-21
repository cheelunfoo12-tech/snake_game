"""Snake entity with input buffering, movement logic, and power-up modifiers."""

from collections import deque
from typing import Sequence

from src.config import (
    FREEZE_EFFECT_DURATION_SEC,
    GHOST_EFFECT_DURATION_SEC,
    GRID_COLUMNS,
    GRID_ROWS,
)


class Snake:
    """Represents the player-controlled snake on the grid."""

    def __init__(self, start_col: int = GRID_COLUMNS // 2, start_row: int = GRID_ROWS // 2) -> None:
        self.segments: list[list[int]] = [[start_col, start_row]]
        self.length: int = 1
        self.current_direction: tuple[int, int] = (0, 0)
        self.input_queue: deque[tuple[int, int]] = deque(maxlen=2)

        # Power-up effect timers (seconds remaining)
        self.freeze_timer: float = 0.0
        self.ghost_timer: float = 0.0

    @property
    def head(self) -> list[int]:
        """Returns the current head position [col, row]."""
        return self.segments[-1]

    @property
    def is_ghost(self) -> bool:
        """True if ghost mode is currently active (allows passing through tail)."""
        return self.ghost_timer > 0.0

    @property
    def is_frozen(self) -> bool:
        """True if freeze slow-motion is currently active."""
        return self.freeze_timer > 0.0

    def enqueue_direction(self, new_dir: tuple[int, int]) -> None:
        """Enqueues a directional change, preventing 180-degree immediate turns."""
        last_dir = self.input_queue[-1] if self.input_queue else self.current_direction

        # Ignore if reversing or identical
        if (new_dir[0] == -last_dir[0] and new_dir[1] == -last_dir[1]) and (last_dir != (0, 0)):
            return
        if new_dir == last_dir:
            return

        self.input_queue.append(new_dir)

    def update_timers(self, dt: float) -> None:
        """Decrements active power-up timers."""
        if self.freeze_timer > 0.0:
            self.freeze_timer = max(0.0, self.freeze_timer - dt)
        if self.ghost_timer > 0.0:
            self.ghost_timer = max(0.0, self.ghost_timer - dt)

    def apply_freeze(self, duration: float = FREEZE_EFFECT_DURATION_SEC) -> None:
        """Activates or refreshes freeze slow-motion."""
        self.freeze_timer = max(self.freeze_timer, duration)

    def apply_ghost(self, duration: float = GHOST_EFFECT_DURATION_SEC) -> None:
        """Activates or refreshes ghost pass-through ability."""
        self.ghost_timer = max(self.ghost_timer, duration)

    def step(self) -> tuple[int, int]:
        """Advances the snake one grid step forward based on direction."""
        if self.input_queue:
            self.current_direction = self.input_queue.popleft()

        dx, dy = self.current_direction
        if dx == 0 and dy == 0:
            return self.head[0], self.head[1]

        new_head = [self.head[0] + dx, self.head[1] + dy]
        self.segments.append(new_head)

        if len(self.segments) > self.length:
            del self.segments[0]

        return new_head[0], new_head[1]

    def grow(self, amount: int = 1) -> None:
        """Increases the snake's target length."""
        self.length += amount

    def check_wall_collision(self) -> bool:
        """Checks if the snake head collided with the grid boundaries."""
        head_x, head_y = self.head
        return head_x < 0 or head_x >= GRID_COLUMNS or head_y < 0 or head_y >= GRID_ROWS

    def check_self_collision(self) -> bool:
        """Checks if the head overlaps any segment of the body. Ignored in ghost mode."""
        if self.is_ghost or len(self.segments) <= 3:
            return False
        return self.head in self.segments[:-1]

    def occupies(self, col: int, row: int) -> bool:
        """Checks if a given coordinate is occupied by the snake."""
        return [col, row] in self.segments
