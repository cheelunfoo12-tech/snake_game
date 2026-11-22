"""Automated unit and integration verification for Neon Snake Remastered."""

import os
import sys

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Run headless without opening window or audio hardware
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()

from src.config import FruitType, GRID_COLUMNS, GRID_ROWS, GameMode
from src.entities.snake import Snake
from src.entities.food import FoodManager
from src.entities.particles import ParticleSystem
from src.entities.obstacles import ObstacleManager, QuantumPortal
from src.entities.ai_controller import AIController
from src.states.state_machine import StateMachine, BaseState


def test_snake_movement_and_growth():
    snake = Snake(10, 10)
    assert snake.head == [10, 10]
    assert snake.length == 1

    snake.enqueue_direction((1, 0))
    snake.step()
    assert snake.head == [11, 10]
    assert len(snake.segments) == 1

    snake.grow(2)
    snake.step()
    assert snake.head == [12, 10]
    assert len(snake.segments) == 2
    snake.step()
    assert snake.head == [13, 10]
    assert len(snake.segments) == 3


def test_direction_buffering_prevents_reversal():
    snake = Snake(10, 10)
    snake.enqueue_direction((1, 0))
    snake.step()

    # Immediate reversal ignored
    snake.enqueue_direction((-1, 0))
    assert len(snake.input_queue) == 0

    # Rapid corner turn queued
    snake.enqueue_direction((0, -1))
    snake.enqueue_direction((-1, 0))
    assert len(snake.input_queue) == 2


def test_wall_and_self_collision():
    snake = Snake(GRID_COLUMNS - 1, 10)
    snake.enqueue_direction((1, 0))
    snake.step()
    assert snake.check_wall_collision() is True

    body_snake = Snake(10, 10)
    body_snake.segments = [[10, 10], [10, 11], [11, 11], [11, 10], [10, 10]]
    assert body_snake.check_self_collision() is True

    body_snake.apply_ghost(5.0)
    assert body_snake.is_ghost is True
    assert body_snake.check_self_collision() is False


def test_quantum_portal_teleportation():
    portal = QuantumPortal(gate_a=(10, 10), gate_b=(25, 25))
    snake = Snake(9, 10, initial_dir=(1, 0))

    # Stepping from (9, 10) moving right onto (10, 10) triggers teleportation
    new_head = snake.step(portal)
    # Portal transports to gate_b (25, 25) + direction (1, 0) = (26, 25)
    assert new_head == (26, 25)
    assert snake.just_teleported is True


def test_obstacle_manager_and_progressive_morphing():
    obs_mgr = ObstacleManager(GameMode.CLASSIC)
    assert len(obs_mgr.obstacles) == 0
    assert obs_mgr.portal is None

    # Progressive morphing tier 2
    obs_mgr.update_progressive(50)
    assert len(obs_mgr.obstacles) > 0

    # Progressive morphing tier 3
    obs_mgr.update_progressive(85)
    assert obs_mgr.portal is not None


def test_ai_controller_pathfinding():
    ai_snake = Snake(15, 15, player_id=2, initial_dir=(-1, 0))
    player_snake = Snake(5, 5, player_id=1, initial_dir=(1, 0))
    controller = AIController(ai_snake)

    # Food to the left of AI
    next_move = controller.compute_next_move(player_snake, [12, 15], obstacles=set())
    assert next_move is not None
    # Next move should be towards the food
    assert next_move in [(-1, 0), (0, -1), (0, 1)]


def test_food_manager_multi_snake():
    s1 = Snake(10, 10)
    s2 = Snake(20, 20)
    food_mgr = FoodManager()
    food_mgr.reset([s1, s2])

    assert food_mgr.regular_food is not None
    assert food_mgr.regular_food not in (s1.segments + s2.segments)


if __name__ == "__main__":
    test_snake_movement_and_growth()
    test_direction_buffering_prevents_reversal()
    test_wall_and_self_collision()
    test_quantum_portal_teleportation()
    test_obstacle_manager_and_progressive_morphing()
    test_ai_controller_pathfinding()
    test_food_manager_multi_snake()
    print("ALL TESTS PASSED SUCCESSFULLY!")
