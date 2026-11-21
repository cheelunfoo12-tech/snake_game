"""Pause screen state with translucent dark overlay and controls."""

import pygame

from src.audio import midi_synth
from src.config import CYAN, GRAY, HEIGHT, WHITE, WIDTH
from src.renderer import NeonRenderer
from src.states.state_machine import BaseState, StateMachine


class PauseState(BaseState):
    """Pause menu preserving underlying gameplay state."""

    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.overlay_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay_surf.fill((6, 10, 22, 185))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_SPACE):
                self.state_machine.change_state("play", {"resume": True})
            elif event.key == pygame.K_q:
                self.state_machine.change_state("menu")
            elif event.key == pygame.K_m:
                midi_synth.toggle_mute()

    def update(self, dt: float) -> None:
        pass

    def draw(self, renderer: NeonRenderer) -> None:
        # Draw translucent overlay
        renderer.screen.blit(self.overlay_surf, (0, 0))

        # Pause Typography
        renderer.draw_text("PAUSED", renderer.title_font, CYAN, WIDTH // 2, HEIGHT // 2 - 60)
        renderer.draw_text("Press P or Esc to Resume", renderer.heading_font, WHITE, WIDTH // 2, HEIGHT // 2 + 10)
        renderer.draw_text("Q: Return to Main Menu  •  M: Toggle Audio", renderer.small_font, GRAY, WIDTH // 2, HEIGHT // 2 + 65)
