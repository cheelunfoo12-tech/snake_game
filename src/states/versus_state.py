"""Versus Duel mode state supporting Player vs AI Rival or Local 2-Player."""

import pygame

from src.audio import MIDI_MUSIC_EVENT, MIDI_NOTE_OFF_EVENT, midi_synth
from src.config import (
    AMBER,
    BACKGROUND,
    CELL_SIZE,
    CYAN,
    DARK_AMBER,
    DARK_GREEN,
    FRUIT_SPECS,
    FruitType,
    GOLD,
    GameMode,
    SPEED_LEVELS,
    VERSUS_ROUNDS_TO_WIN,
    VERSUS_SCORE_TARGET,
    WHITE,
    WIDTH,
    HEIGHT,
)
from src.entities.ai_controller import AIController
from src.entities.food import FoodManager
from src.entities.obstacles import ObstacleManager
from src.entities.particles import ParticleSystem
from src.entities.snake import Snake
from src.renderer import NeonRenderer
from src.states.state_machine import BaseState, StateMachine


class VersusState(BaseState):
    """Versus Duel state (Best of 3 rounds) with AI rival or local 2-player support."""

    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.is_ai: bool = True
        self.p1_rounds: int = 0
        self.p2_rounds: int = 0
        self.p1_score: int = 0
        self.p2_score: int = 0

        self.p1: Snake = Snake()
        self.p2: Snake = Snake()
        self.ai_controller: AIController | None = None
        self.obstacle_mgr: ObstacleManager = ObstacleManager(GameMode.VERSUS_DUEL)
        self.food_mgr: FoodManager = FoodManager()
        self.particles: ParticleSystem = ParticleSystem()

        self.move_accumulator: float = 0.0
        self.pulse_frame: int = 0
        self.round_in_progress: bool = True
        self.round_delay_timer: float = 0.0
        self.round_banner: str = ""

    def enter(self, params: dict | None = None) -> None:
        params = params or {}
        if params.get("resume"):
            self.move_accumulator = 0.0
            return

        self.is_ai = params.get("is_ai", True)
        self.p1_rounds = 0
        self.p2_rounds = 0
        self.p1_score = 0
        self.p2_score = 0
        self._start_new_round()

    def _start_new_round(self) -> None:
        """Initializes a new round, resetting snake positions and obstacles."""
        self.obstacle_mgr = ObstacleManager(GameMode.VERSUS_DUEL)
        self.p1 = Snake(
            start_col=8,
            start_row=15,
            player_id=1,
            head_color=CYAN,
            body_color=DARK_GREEN,
            initial_dir=(1, 0),
        )
        self.p2 = Snake(
            start_col=31,
            start_row=15,
            player_id=2,
            head_color=AMBER,
            body_color=DARK_AMBER,
            initial_dir=(-1, 0),
        )
        self.ai_controller = AIController(self.p2) if self.is_ai else None

        self.food_mgr.reset([self.p1, self.p2], self.obstacle_mgr.get_all_occupied())
        self.particles.clear()
        self.move_accumulator = 0.0
        self.pulse_frame = 0
        self.round_in_progress = True
        self.round_delay_timer = 0.0
        self.round_banner = ""

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            # Player 1: WASD
            if event.key == pygame.K_a:
                self.p1.enqueue_direction((-1, 0))
            elif event.key == pygame.K_d:
                self.p1.enqueue_direction((1, 0))
            elif event.key == pygame.K_w:
                self.p1.enqueue_direction((0, -1))
            elif event.key == pygame.K_s:
                self.p1.enqueue_direction((0, 1))

            # Player 2: Arrow Keys (Only if not AI)
            if not self.is_ai:
                if event.key == pygame.K_LEFT:
                    self.p2.enqueue_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    self.p2.enqueue_direction((1, 0))
                elif event.key == pygame.K_UP:
                    self.p2.enqueue_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    self.p2.enqueue_direction((0, 1))

            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                self.state_machine.change_state("pause")
            elif event.key == pygame.K_m:
                midi_synth.toggle_mute()

        elif event.type == MIDI_NOTE_OFF_EVENT:
            midi_synth.release_notes()
        elif event.type == MIDI_MUSIC_EVENT:
            midi_synth.music_tick()

    def update(self, dt: float) -> None:
        self.pulse_frame += 1
        self.particles.update(dt)

        if not self.round_in_progress:
            self.round_delay_timer -= dt
            if self.round_delay_timer <= 0.0:
                if self.p1_rounds >= VERSUS_ROUNDS_TO_WIN or self.p2_rounds >= VERSUS_ROUNDS_TO_WIN:
                    self._on_match_complete()
                else:
                    self._start_new_round()
            return

        self.p1.update_timers(dt)
        self.p2.update_timers(dt)
        self.food_mgr.update(dt)
        if self.obstacle_mgr.portal:
            self.obstacle_mgr.portal.update()

        # Step tick
        self.move_accumulator += dt
        step_interval = 1.0 / 11.0  # Stable duel movement speed
        if self.move_accumulator >= step_interval:
            self.move_accumulator -= step_interval
            self._step_duel()

    def _step_duel(self) -> None:
        # AI decision for Player 2
        if self.is_ai and self.ai_controller:
            target_food = self.food_mgr.special_fruit.position if self.food_mgr.special_fruit else self.food_mgr.regular_food
            ai_move = self.ai_controller.compute_next_move(
                self.p1,
                target_food,
                self.obstacle_mgr.obstacles,
                self.obstacle_mgr.portal,
            )
            if ai_move:
                self.p2.enqueue_direction(ai_move)

        # Move both snakes
        self.p1.step(self.obstacle_mgr.portal)
        self.p2.step(self.obstacle_mgr.portal)

        # Warp FX
        if self.p1.just_teleported:
            midi_synth.warp()
            cx = self.p1.head[0] * CELL_SIZE + CELL_SIZE // 2
            cy = self.p1.head[1] * CELL_SIZE + CELL_SIZE // 2
            self.particles.emit_burst(cx, cy, CYAN, count=16)

        if self.p2.just_teleported:
            midi_synth.warp()
            cx = self.p2.head[0] * CELL_SIZE + CELL_SIZE // 2
            cy = self.p2.head[1] * CELL_SIZE + CELL_SIZE // 2
            self.particles.emit_burst(cx, cy, AMBER, count=16)

        # Check collisions
        p1_dead = (
            self.p1.check_wall_collision()
            or self.p1.check_self_collision()
            or self.p1.check_obstacle_collision(self.obstacle_mgr.obstacles)
            or self.p1.check_opponent_collision(self.p2)
        )
        p2_dead = (
            self.p2.check_wall_collision()
            or self.p2.check_self_collision()
            or self.p2.check_obstacle_collision(self.obstacle_mgr.obstacles)
            or self.p2.check_opponent_collision(self.p1)
        )

        # Head-on collision
        if self.p1.head == self.p2.head:
            p1_dead = True
            p2_dead = True

        if p1_dead or p2_dead:
            self._end_round(p1_dead, p2_dead)
            return

        # Check food consumption
        consumed_p1 = self.food_mgr.check_consumption(self.p1.head, [self.p1, self.p2], self.obstacle_mgr.get_all_occupied())
        if consumed_p1:
            self._handle_food_eat(self.p1, consumed_p1, is_p1=True)

        consumed_p2 = self.food_mgr.check_consumption(self.p2.head, [self.p1, self.p2], self.obstacle_mgr.get_all_occupied())
        if consumed_p2:
            self._handle_food_eat(self.p2, consumed_p2, is_p1=False)

    def _handle_food_eat(self, snake: Snake, ftype: FruitType, is_p1: bool) -> None:
        cfg = FRUIT_SPECS[ftype]
        if is_p1:
            self.p1_score += cfg.points
            if self.p1_score >= VERSUS_SCORE_TARGET:
                self._end_round(p1_dead=False, p2_dead=True)
                return
        else:
            self.p2_score += cfg.points
            if self.p2_score >= VERSUS_SCORE_TARGET:
                self._end_round(p1_dead=True, p2_dead=False)
                return

        snake.grow(1)
        cx = snake.head[0] * CELL_SIZE + CELL_SIZE // 2
        cy = snake.head[1] * CELL_SIZE + CELL_SIZE // 2
        self.particles.emit_burst(cx, cy, cfg.color, count=16)

        if ftype == FruitType.REGULAR:
            midi_synth.eat_regular()
        elif ftype == FruitType.GOLDEN:
            midi_synth.eat_golden()
        elif ftype == FruitType.FREEZE:
            snake.apply_freeze()
            midi_synth.eat_freeze()
        elif ftype == FruitType.GHOST:
            snake.apply_ghost()
            midi_synth.eat_ghost()

    def _end_round(self, p1_dead: bool, p2_dead: bool) -> None:
        self.round_in_progress = False
        self.round_delay_timer = 2.2
        midi_synth.death()

        if p1_dead and p2_dead:
            self.round_banner = "ROUND DRAW!"
            self.particles.emit_death_shards(self.p1.segments, CYAN)
            self.particles.emit_death_shards(self.p2.segments, AMBER)
        elif p1_dead:
            self.p2_rounds += 1
            rival_name = "AI BOT" if self.is_ai else "PLAYER 2"
            self.round_banner = f"{rival_name} WINS THE ROUND!"
            self.particles.emit_death_shards(self.p1.segments, CYAN)
            midi_synth.round_win()
        else:
            self.p1_rounds += 1
            self.round_banner = "PLAYER 1 WINS THE ROUND!"
            self.particles.emit_death_shards(self.p2.segments, AMBER)
            midi_synth.round_win()

    def _on_match_complete(self) -> None:
        winner = "Player 1" if self.p1_rounds >= VERSUS_ROUNDS_TO_WIN else ("AI Bot" if self.is_ai else "Player 2")
        self.state_machine.change_state(
            "game_over",
            {
                "score": max(self.p1_score, self.p2_score),
                "high_score": max(self.p1_score, self.p2_score),
                "level": 1,
                "winner_text": f"★ {winner.upper()} IS THE CHAMPION! ★",
            },
        )

    def draw(self, renderer: NeonRenderer) -> None:
        renderer.screen.fill(BACKGROUND)
        renderer.draw_grid_lines()
        renderer.draw_obstacles(self.obstacle_mgr.obstacles)
        renderer.draw_portals(self.obstacle_mgr.portal, self.pulse_frame)
        renderer.draw_foods(self.food_mgr, self.pulse_frame)
        renderer.draw_snake(self.p1, self.pulse_frame)
        renderer.draw_snake(self.p2, self.pulse_frame)
        self.particles.draw(renderer.screen)

        renderer.draw_versus_hud(
            self.p1_score,
            self.p2_score,
            self.p1_rounds,
            self.p2_rounds,
            self.is_ai,
            midi_synth.is_muted,
        )

        if not self.round_in_progress and self.round_banner:
            overlay = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
            overlay.fill((6, 10, 22, 210))
            renderer.screen.blit(overlay, (0, HEIGHT // 2 - 40))
            renderer.draw_text(self.round_banner, renderer.heading_font, GOLD, WIDTH // 2, HEIGHT // 2)
