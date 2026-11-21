"""Active gameplay state running at 60 FPS with accumulator-based snake movement."""

import pygame

from src.audio import (
    MIDI_MUSIC_EVENT,
    MIDI_NOTE_OFF_EVENT,
    midi_synth,
)
from src.config import (
    BACKGROUND,
    CELL_SIZE,
    FRUIT_SPECS,
    FruitType,
    HIGH_SCORE_FILE,
    SPEED_LEVELS,
)
from src.entities.food import FoodManager
from src.entities.particles import ParticleSystem
from src.entities.snake import Snake
from src.renderer import NeonRenderer
from src.states.state_machine import BaseState, StateMachine


class PlayState(BaseState):
    """Core play state with smooth rendering and fixed-step grid movement."""

    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.level: int = 5
        self.snake: Snake = Snake()
        self.food_mgr: FoodManager = FoodManager()
        self.particles: ParticleSystem = ParticleSystem()
        self.score: int = 0
        self.high_score: int = self._load_high_score()
        self.move_accumulator: float = 0.0
        self.pulse_frame: int = 0
        self.is_paused: bool = False

    def enter(self, params: dict | None = None) -> None:
        params = params or {}
        if params.get("resume"):
            self.move_accumulator = 0.0
            return

        self.level = params.get("level", self.level)
        self.snake = Snake()
        self.food_mgr.reset(self.snake)
        self.particles.clear()
        self.score = 0
        self.high_score = self._load_high_score()
        self.move_accumulator = 0.0
        self.pulse_frame = 0
        self.is_paused = False

    def _load_high_score(self) -> int:
        try:
            return int(HIGH_SCORE_FILE.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return 0

    def _save_high_score(self, score: int) -> None:
        try:
            HIGH_SCORE_FILE.write_text(str(score), encoding="utf-8")
        except OSError:
            pass

    def _get_step_interval(self) -> float:
        """Calculates seconds per grid movement step based on level, score, and freeze mode."""
        base_speed = SPEED_LEVELS.get(self.level, 12.0)
        # Gentle dynamic speed ramp based on score
        current_speed = min(24.0, base_speed + (self.score // 60) * 0.5)

        # Freeze mode halves movement speed
        if self.snake.is_frozen:
            current_speed *= 0.5

        return 1.0 / max(3.0, current_speed)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.snake.enqueue_direction((-1, 0))
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.snake.enqueue_direction((1, 0))
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.snake.enqueue_direction((0, -1))
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.snake.enqueue_direction((0, 1))
            elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                self.state_machine.change_state("pause")
            elif event.key == pygame.K_m:
                midi_synth.toggle_mute()

        elif event.type == MIDI_NOTE_OFF_EVENT:
            midi_synth.release_notes()
        elif event.type == MIDI_MUSIC_EVENT:
            midi_synth.music_tick()

    def update(self, dt: float) -> None:
        self.pulse_frame += 1
        self.snake.update_timers(dt)
        self.food_mgr.update(dt)
        self.particles.update(dt)

        # Fixed-rate snake step updates
        self.move_accumulator += dt
        step_interval = self._get_step_interval()
        if self.move_accumulator >= step_interval:
            self.move_accumulator -= step_interval
            self._step_snake()

    def _step_snake(self) -> None:
        self.snake.step()

        # Boundary collision check
        if self.snake.check_wall_collision():
            self._on_game_over()
            return

        # Self-collision check (ignored in ghost mode)
        if self.snake.check_self_collision():
            self._on_game_over()
            return

        # Food collision check
        consumed = self.food_mgr.check_consumption(self.snake.head, self.snake)
        if consumed:
            self._handle_food_consumption(consumed)

    def _handle_food_consumption(self, ftype: FruitType) -> None:
        cfg = FRUIT_SPECS[ftype]
        self.score += cfg.points
        self.snake.grow(1)

        # Emit particle burst at fruit location
        cx = self.snake.head[0] * CELL_SIZE + CELL_SIZE // 2
        cy = self.snake.head[1] * CELL_SIZE + CELL_SIZE // 2
        self.particles.emit_burst(cx, cy, cfg.color, count=22)

        # Apply specific effects and audio
        if ftype == FruitType.REGULAR:
            midi_synth.eat_regular()
        elif ftype == FruitType.GOLDEN:
            midi_synth.eat_golden()
        elif ftype == FruitType.FREEZE:
            self.snake.apply_freeze()
            midi_synth.eat_freeze()
        elif ftype == FruitType.GHOST:
            self.snake.apply_ghost()
            midi_synth.eat_ghost()

        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score(self.high_score)

    def _on_game_over(self) -> None:
        midi_synth.death()
        self.particles.emit_death_shards(self.snake.segments)
        self.state_machine.change_state(
            "game_over",
            {
                "score": self.score,
                "high_score": self.high_score,
                "level": self.level,
            },
        )

    def draw(self, renderer: NeonRenderer) -> None:
        renderer.screen.fill(BACKGROUND)
        renderer.draw_grid_lines()
        renderer.draw_foods(self.food_mgr, self.pulse_frame)
        renderer.draw_snake(self.snake, self.pulse_frame)
        self.particles.draw(renderer.screen)
        renderer.draw_hud(
            self.score,
            self.high_score,
            self.level,
            self.snake,
            self.food_mgr,
            midi_synth.is_muted,
        )
