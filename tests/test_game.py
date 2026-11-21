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

from src.config import FruitType, GRID_COLUMNS, GRID_ROWS
from src.entities.snake import Snake
from src.entities.food import FoodManager
from src.entities.particles import ParticleSystem
from src.states.state_machine import StateMachine, BaseState


def test_snake_movement_and_growth():
    snake = Snake(10, 10)
    assert snake.head == [10, 10]
    assert snake.length == 1

    # Enqueue right
    snake.enqueue_direction((1, 0))
    snake.step()
    assert snake.head == [11, 10]
    assert len(snake.segments) == 1

    # Grow snake
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
    snake.step()  # Moving right

    # Immediate left turn should be rejected
    snake.enqueue_direction((-1, 0))
    assert len(snake.input_queue) == 0

    # Rapid turn (Up then Left) should queue properly
    snake.enqueue_direction((0, -1))
    snake.enqueue_direction((-1, 0))
    assert len(snake.input_queue) == 2


def test_wall_and_self_collision():
    # Wall collision test
    snake = Snake(GRID_COLUMNS - 1, 10)
    snake.enqueue_direction((1, 0))
    snake.step()
    assert snake.check_wall_collision() is True

    # Self collision test
    body_snake = Snake(10, 10)
    body_snake.segments = [[10, 10], [10, 11], [11, 11], [11, 10], [10, 10]]
    assert body_snake.check_self_collision() is True

    # Ghost mode bypasses self collision
    body_snake.apply_ghost(5.0)
    assert body_snake.is_ghost is True
    assert body_snake.check_self_collision() is False


def test_food_manager_and_special_spawns():
    snake = Snake(10, 10)
    food_mgr = FoodManager()
    food_mgr.reset(snake)

    assert food_mgr.regular_food is not None
    assert food_mgr.special_fruit is None

    # Simulate eating 5 regular foods
    for i in range(5):
        food_mgr.on_regular_eaten(snake)

    # Milestone should have spawned a special fruit
    assert food_mgr.special_fruit is not None
    assert food_mgr.special_fruit.fruit_type in (
        FruitType.GOLDEN,
        FruitType.FREEZE,
        FruitType.GHOST,
    )

    # Test expiration countdown
    food_mgr.update(11.0)
    assert food_mgr.special_fruit is None


def test_particle_system():
    ps = ParticleSystem()
    ps.emit_burst(100.0, 100.0, (255, 0, 0), count=10)
    assert len(ps.particles) == 10

    # Updating with large dt should purge expired particles
    ps.update(2.0)
    assert len(ps.particles) == 0


def test_state_machine_transitions():
    class DummyState(BaseState):
        def __init__(self, sm, name):
            super().__init__(sm)
            self.name = name
            self.entered = False

        def enter(self, params=None):
            self.entered = True

        def handle_event(self, event):
            pass

        def update(self, dt):
            pass

        def draw(self, renderer):
            pass

    sm = StateMachine()
    s1 = DummyState(sm, "one")
    s2 = DummyState(sm, "two")
    sm.add_state("one", s1)
    sm.add_state("two", s2)

    sm.change_state("one")
    assert sm.current_state_name == "one"
    assert s1.entered is True

    sm.change_state("two")
    assert sm.current_state_name == "two"
    assert s2.entered is True


if __name__ == "__main__":
    test_snake_movement_and_growth()
    test_direction_buffering_prevents_reversal()
    test_wall_and_self_collision()
    test_food_manager_and_special_spawns()
    test_particle_system()
    test_state_machine_transitions()
    print("ALL TESTS PASSED SUCCESSFULLY!")
