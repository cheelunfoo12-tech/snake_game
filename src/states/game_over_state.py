"""Game Over state displaying final scores, new high score celebrations, and replay controls."""

import pygame

from src.audio import MIDI_NOTE_OFF_EVENT, midi_synth
from src.config import (
    BACKGROUND,
    BUTTON_TEXT,
    CYAN,
    GOLD,
    GRAY,
    PANEL,
    RED,
    WHITE,
    WIDTH,
)
from src.renderer import NeonRenderer
from src.states.state_machine import BaseState, StateMachine


class GameOverState(BaseState):
    """Death and post-game statistics screen."""

    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.score: int = 0
        self.high_score: int = 0
        self.level: int = 5
        self.is_new_high: bool = False
        self.pulse_frame: int = 0

        self.replay_button: pygame.Rect = pygame.Rect(WIDTH // 2 - 150, 400, 300, 54)
        self.menu_button: pygame.Rect = pygame.Rect(WIDTH // 2 - 150, 470, 300, 54)

    def enter(self, params: dict | None = None) -> None:
        params = params or {}
        self.score = params.get("score", 0)
        self.high_score = params.get("high_score", 0)
        self.level = params.get("level", 5)
        self.is_new_high = self.score >= self.high_score and self.score > 0
        self.pulse_frame = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_c):
                self._replay()
            elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                self.state_machine.change_state("menu")
            elif event.key == pygame.K_m:
                midi_synth.toggle_mute()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.replay_button.collidepoint(event.pos):
                self._replay()
            elif self.menu_button.collidepoint(event.pos):
                self.state_machine.change_state("menu")

        elif event.type == MIDI_NOTE_OFF_EVENT:
            midi_synth.release_notes()

    def _replay(self) -> None:
        midi_synth.start()
        self.state_machine.change_state("play", {"level": self.level})

    def update(self, dt: float) -> None:
        self.pulse_frame += 1

    def draw(self, renderer: NeonRenderer) -> None:
        renderer.screen.fill(BACKGROUND)

        # Header
        renderer.draw_text("GAME OVER", renderer.title_font, RED, WIDTH // 2, 130)

        # High score celebration
        if self.is_new_high:
            renderer.draw_text("★ NEW HIGH SCORE! ★", renderer.heading_font, GOLD, WIDTH // 2, 205)
        else:
            renderer.draw_text(f"Level {self.level} Run Complete", renderer.small_font, GRAY, WIDTH // 2, 205)

        # Score stats cards
        renderer.draw_text(f"Score: {self.score}", renderer.heading_font, WHITE, WIDTH // 2, 265)
        renderer.draw_text(f"Best: {self.high_score}", renderer.body_font, GOLD, WIDTH // 2, 315)

        # Replay Button
        renderer.draw_panel(self.replay_button, True)
        renderer.draw_text("PLAY AGAIN (Space)", renderer.body_font, BUTTON_TEXT, self.replay_button.centerx, self.replay_button.centery)

        # Menu Button
        renderer.draw_panel(self.menu_button, False)
        renderer.draw_text("MAIN MENU (Esc)", renderer.body_font, WHITE, self.menu_button.centerx, self.menu_button.centery)
