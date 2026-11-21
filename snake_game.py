"""Neon Snake: Remastered Edition - Main Application Entrypoint."""

import os
import sys
import pygame
import pygame.midi

from src.audio import midi_synth
from src.config import FPS, HEIGHT, WIDTH
from src.renderer import NeonRenderer
from src.states.game_over_state import GameOverState
from src.states.menu_state import MenuState
from src.states.pause_state import PauseState
from src.states.play_state import PlayState
from src.states.state_machine import StateMachine


def main() -> None:
    """Initializes the game engine and executes the deterministic main loop."""
    os.environ["SDL_VIDEO_WINDOW_POS"] = "100,80"
    pygame.init()
    if not pygame.midi.get_init():
        try:
            pygame.midi.init()
        except Exception:
            pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neon Snake: Remastered")
    clock = pygame.time.Clock()

    renderer = NeonRenderer(screen)

    # Initialize state machine
    state_machine = StateMachine()
    state_machine.add_state("menu", MenuState(state_machine))
    state_machine.add_state("play", PlayState(state_machine))
    state_machine.add_state("pause", PauseState(state_machine))
    state_machine.add_state("game_over", GameOverState(state_machine))

    # Start at main menu
    state_machine.change_state("menu")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.1)  # Clamp delta time to avoid large physics steps on window drag

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            state_machine.handle_event(event)

        # 2. State & Visual FX Update
        state_machine.update(dt)
        renderer.update_shake(dt)

        # 3. Render
        state_machine.draw(renderer)
        pygame.display.flip()

    # 4. Clean Shutdown
    midi_synth.close()
    if pygame.midi.get_init():
        try:
            pygame.midi.quit()
        except Exception:
            pass
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
