"""Main Menu state with difficulty selection, fruit legend, and audio toggle."""

import pygame

from src.audio import MIDI_MUSIC_EVENT, midi_synth
from src.config import (
    BACKGROUND,
    BUTTON_TEXT,
    CYAN,
    DARK_GRAY,
    FRUIT_SPECS,
    FruitType,
    GOLD,
    GRAY,
    PANEL,
    PANEL_BORDER,
    RED,
    WHITE,
    WIDTH,
)
from src.renderer import NeonRenderer
from src.states.state_machine import BaseState, StateMachine


class MenuState(BaseState):
    """Main menu and difficulty selection screen."""

    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.selected_level: int = 5
        self.level_buttons: list[pygame.Rect] = [
            pygame.Rect(40 + col * 72, 290, 60, 58) for col in range(10)
        ]
        self.start_button: pygame.Rect = pygame.Rect(WIDTH // 2 - 140, 500, 280, 56)
        self.pulse_frame: int = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_level = max(1, self.selected_level - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_level = min(10, self.selected_level + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_game()
            elif event.key == pygame.K_m:
                midi_synth.toggle_mute()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.collidepoint(event.pos):
                self._start_game()
            for idx, rect in enumerate(self.level_buttons):
                if rect.collidepoint(event.pos):
                    self.selected_level = idx + 1

    def _start_game(self) -> None:
        midi_synth.start()
        pygame.time.set_timer(MIDI_MUSIC_EVENT, 420)
        self.state_machine.change_state("play", {"level": self.selected_level})

    def update(self, dt: float) -> None:
        self.pulse_frame += 1

    def draw(self, renderer: NeonRenderer) -> None:
        renderer.screen.fill(BACKGROUND)

        # Title with neon glow
        renderer.draw_text("NEON SNAKE", renderer.title_font, CYAN, WIDTH // 2, 75)
        renderer.draw_text("REMASTERED EDITION", renderer.small_font, GRAY, WIDTH // 2, 115)

        # Fruit Legend Overview
        self._draw_fruit_legend(renderer)

        # Difficulty Level Select Header
        renderer.draw_text("Choose Starting Speed", renderer.heading_font, WHITE, WIDTH // 2, 255)

        # Level Buttons
        for idx, rect in enumerate(self.level_buttons):
            lvl = idx + 1
            is_selected = lvl == self.selected_level
            renderer.draw_panel(rect, is_selected)
            text_color = BUTTON_TEXT if is_selected else WHITE
            renderer.draw_text(str(lvl), renderer.body_font, text_color, rect.centerx, rect.centery)

        # Speed Tier Description
        speed_names = ("Relaxed", "Easy", "Normal", "Fast", "Extreme")
        name_idx = min(4, (self.selected_level - 1) // 2)
        renderer.draw_text(
            f"Level {self.selected_level}  —  {speed_names[name_idx]} Speed",
            renderer.body_font,
            GOLD,
            WIDTH // 2,
            375,
        )

        # Start Button
        renderer.draw_panel(self.start_button, True)
        renderer.draw_text("START GAME", renderer.body_font, BUTTON_TEXT, self.start_button.centerx, self.start_button.centery)

        # Controls Hint
        renderer.draw_text(
            "Controls: Arrow Keys / WASD  •  P: Pause  •  M: Mute Audio",
            renderer.small_font,
            GRAY,
            WIDTH // 2,
            572,
        )

    def _draw_fruit_legend(self, renderer: NeonRenderer) -> None:
        """Draws a mini showcase of available fruits and their powers."""
        legend_rect = pygame.Rect(60, 145, WIDTH - 120, 75)
        pygame.draw.rect(renderer.screen, PANEL, legend_rect, border_radius=8)
        pygame.draw.rect(renderer.screen, PANEL_BORDER, legend_rect, width=1, border_radius=8)

        legend_items = [
            (FruitType.REGULAR, "Apple (+10)"),
            (FruitType.GOLDEN, "Golden (+30)"),
            (FruitType.FREEZE, "Freeze (Slow)"),
            (FruitType.GHOST, "Ghost (Phase)"),
        ]
        spacing = legend_rect.width // len(legend_items)
        for idx, (ftype, label) in enumerate(legend_items):
            cfg = FRUIT_SPECS[ftype]
            cx = legend_rect.x + idx * spacing + spacing // 2
            cy = legend_rect.y + 24
            pygame.draw.circle(renderer.screen, cfg.color, (cx, cy), 8)
            renderer.draw_text(label, renderer.small_font, WHITE, cx, cy + 24)
