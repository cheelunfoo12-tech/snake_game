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

from src.config import FruitType, GRID_COLUMNS, GRID_MIN_ROW, GRID_ROWS, GameMode
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


def test_wall_and_hud_boundary_collision():
    # Right wall collision
    snake = Snake(GRID_COLUMNS - 1, 10)
    snake.enqueue_direction((1, 0))
    snake.step()
    assert snake.check_wall_collision() is True

    # Top HUD boundary collision (hitting y < GRID_MIN_ROW = 3)
    top_snake = Snake(10, GRID_MIN_ROW)
    assert top_snake.check_wall_collision() is False
    top_snake.enqueue_direction((0, -1))
    top_snake.step()
    assert top_snake.head[1] == GRID_MIN_ROW - 1
    assert top_snake.check_wall_collision() is True

    # Self collision test
    body_snake = Snake(10, 10)
    body_snake.segments = [[10, 10], [10, 11], [11, 11], [11, 10], [10, 10]]
    assert body_snake.check_self_collision() is True

    body_snake.apply_ghost(5.0)
    assert body_snake.is_ghost is True
    assert body_snake.check_self_collision() is False


def test_food_always_within_playable_arena():
    snake = Snake(10, 10)
    food_mgr = FoodManager()

    # Test 50 food spawns to ensure food NEVER spawns in rows 0, 1, 2 (behind HUD)
    for _ in range(50):
        food_mgr.spawn_regular(snake)
        col, row = food_mgr.regular_food
        assert 0 <= col < GRID_COLUMNS
        assert GRID_MIN_ROW <= row < GRID_ROWS, f"Food spawned in HUD row {row}!"

        food_mgr.spawn_special(snake)
        if food_mgr.special_fruit:
            scol, srow = food_mgr.special_fruit.position
            assert 0 <= scol < GRID_COLUMNS
            assert GRID_MIN_ROW <= srow < GRID_ROWS, f"Special fruit spawned in HUD row {srow}!"


def test_quantum_portal_teleportation():
    portal = QuantumPortal(gate_a=(10, 10), gate_b=(25, 25))
    snake = Snake(9, 10, initial_dir=(1, 0))

    new_head = snake.step(portal)
    assert new_head == (26, 25)
    assert snake.just_teleported is True


def test_obstacle_manager_and_progressive_morphing():
    obs_mgr = ObstacleManager(GameMode.CLASSIC)
    assert len(obs_mgr.obstacles) == 0
    assert obs_mgr.portal is None

    obs_mgr.update_progressive(50)
    assert len(obs_mgr.obstacles) > 0
    for col, row in obs_mgr.obstacles:
        assert GRID_MIN_ROW <= row < GRID_ROWS

    obs_mgr.update_progressive(85)
    assert obs_mgr.portal is not None


def test_ai_controller_pathfinding():
    ai_snake = Snake(15, 15, player_id=2, initial_dir=(-1, 0))
    player_snake = Snake(5, 5, player_id=1, initial_dir=(1, 0))
    controller = AIController(ai_snake)

    next_move = controller.compute_next_move(player_snake, [12, 15], obstacles=set())
    assert next_move is not None
    assert next_move in [(-1, 0), (0, -1), (0, 1)]


if __name__ == "__main__":
    test_snake_movement_and_growth()
    test_direction_buffering_prevents_reversal()
    test_wall_and_hud_boundary_collision()
    test_food_always_within_playable_arena()
    test_quantum_portal_teleportation()
    test_obstacle_manager_and_progressive_morphing()
    test_ai_controller_pathfinding()
    print("ALL TESTS PASSED SUCCESSFULLY!")
