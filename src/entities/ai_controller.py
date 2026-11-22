"""Tactical AI Controller with BFS pathfinding, flood-fill safety, and aggressive cut-offs."""

from collections import deque
from typing import Sequence

from src.config import GRID_COLUMNS, GRID_ROWS
from src.entities.obstacles import QuantumPortal
from src.entities.snake import Snake


class AIController:
    """Controls rival snake with pathfinding and aggressive cut-off interception."""

    def __init__(self, ai_snake: Snake) -> None:
        self.snake: Snake = ai_snake
        self.directions: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def compute_next_move(
        self,
        player_snake: Snake,
        food_pos: list[int],
        obstacles: set[tuple[int, int]],
        portal: QuantumPortal | None = None,
    ) -> tuple[int, int] | None:
        """Determines the optimal directional vector for the AI snake."""
        head_x, head_y = self.snake.head
        cur_dir = self.snake.current_direction

        # 1. Build blocked cells set (walls, obstacles, bodies)
        blocked: set[tuple[int, int]] = set(obstacles)
        for seg in self.snake.segments[:-1]:
            if not self.snake.is_ghost:
                blocked.add((seg[0], seg[1]))
        for seg in player_snake.segments:
            blocked.add((seg[0], seg[1]))

        # Filter valid immediate moves that don't reverse
        valid_moves: list[tuple[int, int]] = []
        for dx, dy in self.directions:
            if cur_dir != (0, 0) and dx == -cur_dir[0] and dy == -cur_dir[1]:
                continue
            nx, ny = head_x + dx, head_y + dy
            # Check portal warp
            if portal:
                dest = portal.check_teleport(nx, ny)
                if dest:
                    nx, ny = dest[0] + dx, dest[1] + dy

            if 0 <= nx < GRID_COLUMNS and 0 <= ny < GRID_ROWS and (nx, ny) not in blocked:
                valid_moves.append((dx, dy))

        if not valid_moves:
            return None  # Trapped with nowhere to turn

        if len(valid_moves) == 1:
            return valid_moves[0]

        # 2. Aggressive Cut-off: Check if player is close enough to intercept
        dist_to_player = abs(head_x - player_snake.head[0]) + abs(head_y - player_snake.head[1])
        target_goal = (food_pos[0], food_pos[1])

        if dist_to_player <= 7 and player_snake.current_direction != (0, 0):
            # Project player head 2 steps ahead to cut them off
            pdx, pdy = player_snake.current_direction
            cut_x = player_snake.head[0] + pdx * 2
            cut_y = player_snake.head[1] + pdy * 2
            if 0 <= cut_x < GRID_COLUMNS and 0 <= cut_y < GRID_ROWS and (cut_x, cut_y) not in blocked:
                target_goal = (cut_x, cut_y)

        # 3. BFS Shortest Path to Target Goal
        best_move = self._bfs_shortest_path(self.snake.head, target_goal, valid_moves, blocked, portal)
        if best_move and self._has_sufficient_space(head_x + best_move[0], head_y + best_move[1], blocked):
            return best_move

        # 4. If direct path is trapped or blocked, pick valid move with largest free space (flood-fill)
        best_space = -1
        chosen_move = valid_moves[0]
        for move in valid_moves:
            nx, ny = head_x + move[0], head_y + move[1]
            space = self._flood_fill_count(nx, ny, blocked, max_count=self.snake.length + 10)
            if space > best_space:
                best_space = space
                chosen_move = move

        return chosen_move

    def _bfs_shortest_path(
        self,
        start: list[int],
        goal: tuple[int, int],
        valid_first_moves: list[tuple[int, int]],
        blocked: set[tuple[int, int]],
        portal: QuantumPortal | None,
    ) -> tuple[int, int] | None:
        """Finds first step towards goal using BFS."""
        queue: deque[tuple[int, int, tuple[int, int]]] = deque()
        visited: set[tuple[int, int]] = set(blocked)

        for dx, dy in valid_first_moves:
            nx, ny = start[0] + dx, start[1] + dy
            if (nx, ny) == goal:
                return (dx, dy)
            visited.add((nx, ny))
            queue.append((nx, ny, (dx, dy)))

        while queue:
            cx, cy, initial_step = queue.popleft()
            if (cx, cy) == goal:
                return initial_step

            for dx, dy in self.directions:
                nx, ny = cx + dx, cy + dy
                if portal:
                    dest = portal.check_teleport(nx, ny)
                    if dest:
                        nx, ny = dest[0] + dx, dest[1] + dy

                if 0 <= nx < GRID_COLUMNS and 0 <= ny < GRID_ROWS and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, initial_step))

        return None

    def _flood_fill_count(self, start_x: int, start_y: int, blocked: set[tuple[int, int]], max_count: int = 40) -> int:
        """Counts reachable cells from a candidate coordinate to prevent entering dead ends."""
        visited: set[tuple[int, int]] = set(blocked)
        queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
        visited.add((start_x, start_y))
        count = 0

        while queue and count < max_count:
            cx, cy = queue.popleft()
            count += 1
            for dx, dy in self.directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < GRID_COLUMNS and 0 <= ny < GRID_ROWS and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return count

    def _has_sufficient_space(self, start_x: int, start_y: int, blocked: set[tuple[int, int]]) -> bool:
        free_space = self._flood_fill_count(start_x, start_y, blocked, max_count=self.snake.length + 5)
        return free_space >= min(self.snake.length, 15)
