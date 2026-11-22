"""Snake entity supporting single-player, multi-snake duels, and portal traversal."""

from collections import deque
from typing import Sequence

from src.config import (
    CYAN,
    DARK_GREEN,
    FREEZE_EFFECT_DURATION_SEC,
    GHOST_EFFECT_DURATION_SEC,
    GRID_COLUMNS,
    GRID_MIN_ROW,
    GRID_ROWS,
)
from src.entities.obstacles import QuantumPortal


class Snake:
    """Represents a player-controlled or AI-controlled snake on the grid."""

    def __init__(
        self,
        start_col: int = GRID_COLUMNS // 2,
        start_row: int = (GRID_MIN_ROW + GRID_ROWS) // 2,
        player_id: int = 1,
        head_color: tuple[int, int, int] = CYAN,
        body_color: tuple[int, int, int] = DARK_GREEN,
        initial_dir: tuple[int, int] = (0, 0),
    ) -> None:
        self.player_id: int = player_id
        self.head_color: tuple[int, int, int] = head_color
        self.body_color: tuple[int, int, int] = body_color
        self.segments: list[list[int]] = [[start_col, start_row]]
        self.length: int = 1
        self.current_direction: tuple[int, int] = initial_dir
        self.input_queue: deque[tuple[int, int]] = deque(maxlen=2)

        # Power-up effect timers (seconds remaining)
        self.freeze_timer: float = 0.0
        self.ghost_timer: float = 0.0

        # Teleport flag for particle trigger
        self.just_teleported: bool = False

    @property
    def head(self) -> list[int]:
        """Returns the current head position [col, row]."""
        return self.segments[-1]

    @property
    def is_ghost(self) -> bool:
        """True if ghost mode is active (allows passing through tail)."""
        return self.ghost_timer > 0.0

    @property
    def is_frozen(self) -> bool:
        """True if freeze slow-motion is active."""
        return self.freeze_timer > 0.0

    def enqueue_direction(self, new_dir: tuple[int, int]) -> None:
        """Enqueues a directional change, preventing 180-degree turns."""
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
        self.freeze_timer = max(self.freeze_timer, duration)

    def apply_ghost(self, duration: float = GHOST_EFFECT_DURATION_SEC) -> None:
        self.ghost_timer = max(self.ghost_timer, duration)

    def step(self, portal: QuantumPortal | None = None) -> tuple[int, int]:
        """Advances the snake one grid step forward, handling quantum portals if encountered."""
        self.just_teleported = False

        if self.input_queue:
            self.current_direction = self.input_queue.popleft()

        dx, dy = self.current_direction
        if dx == 0 and dy == 0:
            return self.head[0], self.head[1]

        target_col = self.head[0] + dx
        target_row = self.head[1] + dy

        # Quantum Portal check
        if portal:
            dest = portal.check_teleport(target_col, target_row)
            if dest:
                # Teleport to partner gate and step outward with preserved direction
                target_col, target_row = dest[0] + dx, dest[1] + dy
                self.just_teleported = True

        new_head = [target_col, target_row]
        self.segments.append(new_head)

        if len(self.segments) > self.length:
            del self.segments[0]

        return new_head[0], new_head[1]

    def grow(self, amount: int = 1) -> None:
        self.length += amount

    def check_wall_collision(self) -> bool:
        """Checks if snake head collided with grid boundaries or top HUD banner."""
        head_x, head_y = self.head
        return (
            head_x < 0
            or head_x >= GRID_COLUMNS
            or head_y < GRID_MIN_ROW
            or head_y >= GRID_ROWS
        )

    def check_self_collision(self) -> bool:
        """Checks if head overlaps body segments. Ignored in ghost mode."""
        if self.is_ghost or len(self.segments) <= 3:
            return False
        return self.head in self.segments[:-1]

    def check_obstacle_collision(self, obstacles: set[tuple[int, int]]) -> bool:
        """Checks if snake head collided with an inner barrier block."""
        return (self.head[0], self.head[1]) in obstacles

    def check_opponent_collision(self, opponent: "Snake") -> bool:
        """Checks if snake head collided into any part of opponent's snake body."""
        return self.head in opponent.segments

    def occupies(self, col: int, row: int) -> bool:
        return [col, row] in self.segments
