"""Arena layouts, obstacle barriers, and paired quantum teleporters."""

from typing import Iterable
from src.config import (
    GRID_COLUMNS,
    GRID_MIN_ROW,
    GRID_ROWS,
    PORTAL_PAIR_A,
    PORTAL_PAIR_B,
    GameMode,
)


class QuantumPortal:
    """Paired color-coded teleporter gates that instantly warp traversing entities."""

    def __init__(self, gate_a: tuple[int, int] = PORTAL_PAIR_A, gate_b: tuple[int, int] = PORTAL_PAIR_B) -> None:
        self.gate_a: tuple[int, int] = gate_a
        self.gate_b: tuple[int, int] = gate_b
        self.cooldown_a: int = 0
        self.cooldown_b: int = 0

    def update(self) -> None:
        """Ticks down teleportation cooldowns."""
        if self.cooldown_a > 0:
            self.cooldown_a -= 1
        if self.cooldown_b > 0:
            self.cooldown_b -= 1

    def check_teleport(self, col: int, row: int) -> tuple[int, int] | None:
        """Checks if a cell triggers teleportation. Returns destination coordinates or None."""
        pos = (col, row)
        if pos == self.gate_a and self.cooldown_a == 0:
            self.cooldown_b = 3  # Prevent immediate return warp
            return self.gate_b
        if pos == self.gate_b and self.cooldown_b == 0:
            self.cooldown_a = 3
            return self.gate_a
        return None


class ObstacleManager:
    """Manages active inner barriers, progressive arena morphing, and quantum portals."""

    def __init__(self, mode: GameMode = GameMode.CLASSIC) -> None:
        self.mode: GameMode = mode
        self.obstacles: set[tuple[int, int]] = set()
        self.portal: QuantumPortal | None = None
        self.current_tier: int = 1
        self._init_layout()

    def _init_layout(self) -> None:
        self.obstacles.clear()
        self.portal = None
        self.current_tier = 1

        if self.mode == GameMode.MAZE_SURVIVAL:
            self._build_maze_layout()
        elif self.mode == GameMode.VERSUS_DUEL:
            self._build_versus_layout()
        elif self.mode == GameMode.TIME_ATTACK:
            self.portal = QuantumPortal()
        elif self.mode == GameMode.CLASSIC:
            pass

    def _build_versus_layout(self) -> None:
        """Symmetric arena for 1v1 duels with paired portals and center divider pillars."""
        self.portal = QuantumPortal(PORTAL_PAIR_A, PORTAL_PAIR_B)
        for r in range(11, 14):
            self.obstacles.add((GRID_COLUMNS // 2, r))
        for r in range(19, 22):
            self.obstacles.add((GRID_COLUMNS // 2, r))

    def _build_maze_layout(self) -> None:
        """Dense neon labyrinth layout with geometric corridors strictly within bounds."""
        for c in range(8, 16):
            self.obstacles.add((c, 9))
            self.obstacles.add((GRID_COLUMNS - 1 - c, GRID_ROWS - 5))
        for r in range(9, 16):
            self.obstacles.add((15, r))
            self.obstacles.add((GRID_COLUMNS - 16, GRID_ROWS - 1 - (r - 4)))

        # Center chamber pillars
        for c in (18, 21):
            for r in range(13, 19):
                self.obstacles.add((c, r))

        self.portal = QuantumPortal(PORTAL_PAIR_A, PORTAL_PAIR_B)

    def update_progressive(self, score: int) -> bool:
        """Morphs the arena in Classic mode as the player hits score tiers."""
        if self.mode != GameMode.CLASSIC:
            return False

        changed = False
        # Tier 2: Score 40 -> Introduce central neon pillar barriers
        if score >= 40 and self.current_tier < 2:
            self.current_tier = 2
            for c in (12, 27):
                for r in range(9, 14):
                    self.obstacles.add((c, r))
                for r in range(18, 23):
                    self.obstacles.add((c, r))
            changed = True

        # Tier 3: Score 80 -> Materialize Quantum Portals
        if score >= 80 and self.current_tier < 3:
            self.current_tier = 3
            self.portal = QuantumPortal(PORTAL_PAIR_A, PORTAL_PAIR_B)
            changed = True

        return changed

    def is_blocked(self, col: int, row: int) -> bool:
        return (col, row) in self.obstacles

    def get_all_occupied(self) -> set[tuple[int, int]]:
        occupied = set(self.obstacles)
        if self.portal:
            occupied.add(self.portal.gate_a)
            occupied.add(self.portal.gate_b)
        return occupied
