"""Game configuration, constants, and color definitions."""

from enum import Enum
from pathlib import Path
from typing import NamedTuple

# Screen & Grid
WIDTH: int = 800
HEIGHT: int = 600
FPS: int = 60
GRID_COLUMNS: int = 40
GRID_ROWS: int = 30
CELL_SIZE: int = 20

# Colors (RGB)
BACKGROUND: tuple[int, int, int] = (6, 10, 22)
PANEL: tuple[int, int, int] = (26, 36, 69)
PANEL_BORDER: tuple[int, int, int] = (45, 60, 105)
CYAN: tuple[int, int, int] = (77, 230, 255)
GREEN: tuple[int, int, int] = (77, 255, 163)
DARK_GREEN: tuple[int, int, int] = (20, 97, 64)
RED: tuple[int, int, int] = (255, 92, 122)
GOLD: tuple[int, int, int] = (255, 201, 87)
ICE_BLUE: tuple[int, int, int] = (150, 230, 255)
GHOST_PURPLE: tuple[int, int, int] = (220, 120, 255)
WHITE: tuple[int, int, int] = (242, 250, 255)
GRAY: tuple[int, int, int] = (140, 153, 184)
DARK_GRAY: tuple[int, int, int] = (40, 50, 75)
BUTTON_TEXT: tuple[int, int, int] = (8, 20, 31)

# P2 / AI Rival Colors
AMBER: tuple[int, int, int] = (255, 170, 40)
DARK_AMBER: tuple[int, int, int] = (130, 80, 15)

# Quantum Portal Colors
PORTAL_BLUE: tuple[int, int, int] = (60, 150, 255)
PORTAL_VIOLET: tuple[int, int, int] = (210, 80, 255)
OBSTACLE_COLOR: tuple[int, int, int] = (180, 50, 80)
OBSTACLE_BORDER: tuple[int, int, int] = (255, 90, 120)

# High Score Persistence
HIGH_SCORE_FILE: Path = Path(__file__).resolve().parent.parent / "high_score.txt"


class GameMode(Enum):
    """Game modes available in the game."""
    CLASSIC = "classic"
    TIME_ATTACK = "time_attack"
    MAZE_SURVIVAL = "maze_survival"
    VERSUS_DUEL = "versus_duel"


class FruitType(Enum):
    """Types of fruits available in the game."""
    REGULAR = "regular"
    GOLDEN = "golden"
    FREEZE = "freeze"
    GHOST = "ghost"


class FruitConfig(NamedTuple):
    """Configuration attributes for each fruit type."""
    name: str
    points: int
    color: tuple[int, int, int]
    duration_sec: float
    description: str


FRUIT_SPECS: dict[FruitType, FruitConfig] = {
    FruitType.REGULAR: FruitConfig(
        name="Apple",
        points=10,
        color=RED,
        duration_sec=0.0,
        description="+10 Points",
    ),
    FruitType.GOLDEN: FruitConfig(
        name="Golden Apple",
        points=30,
        color=GOLD,
        duration_sec=10.0,
        description="+30 Bonus Points",
    ),
    FruitType.FREEZE: FruitConfig(
        name="Freeze Berry",
        points=15,
        color=ICE_BLUE,
        duration_sec=10.0,
        description="Slow Motion (6s)",
    ),
    FruitType.GHOST: FruitConfig(
        name="Ghost Berry",
        points=15,
        color=GHOST_PURPLE,
        duration_sec=10.0,
        description="Pass Through Body (6s)",
    ),
}

# Gameplay Balance
SPECIAL_FRUIT_SPAWN_INTERVAL: int = 5
SPECIAL_FRUIT_LIFESPAN_SEC: float = 10.0
FREEZE_EFFECT_DURATION_SEC: float = 6.0
GHOST_EFFECT_DURATION_SEC: float = 6.0

# Time Attack Settings
TIME_ATTACK_START_SEC: float = 45.0
TIME_ATTACK_REGULAR_BONUS_SEC: float = 3.0
TIME_ATTACK_SPECIAL_BONUS_SEC: float = 5.0

# Versus Duel Settings
VERSUS_ROUNDS_TO_WIN: int = 2
VERSUS_SCORE_TARGET: int = 100

# Speed levels: Level 1..10 maps to steps per second
SPEED_LEVELS: dict[int, float] = {
    1: 6.0,
    2: 7.5,
    3: 9.0,
    4: 10.5,
    5: 12.0,
    6: 14.0,
    7: 16.0,
    8: 18.0,
    9: 20.0,
    10: 23.0,
}

# Quantum Portal Locations
PORTAL_PAIR_A: tuple[int, int] = (6, 15)
PORTAL_PAIR_B: tuple[int, int] = (33, 15)
