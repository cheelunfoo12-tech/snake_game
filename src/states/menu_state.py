"""Main Menu state with 4 game mode selectors, Versus opponent toggles, and audio controls."""

import pygame

from src.audio import MIDI_MUSIC_EVENT, midi_synth
from src.config import (
    AMBER,
    BACKGROUND,
    BUTTON_TEXT,
    CYAN,
    DARK_GRAY,
    FRUIT_SPECS,
    FruitType,
    GOLD,
    GRAY,
    GameMode,
    PANEL,
    PANEL_BORDER,
    RED,
    WHITE,
    WIDTH,
)
from src.renderer import NeonRenderer
from src.states.state_machine import BaseState, StateMachine


class MenuState(BaseState):
    """Main menu with 4 distinct game mode options and Versus Duel settings."""

    def __init__(self, state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.selected_mode: GameMode = GameMode.CLASSIC
        self.versus_is_ai: bool = True
        self.selected_level: int = 5
        self.pulse_frame: int = 0

        # Mode selection buttons
        self.mode_buttons: list[tuple[GameMode, str, pygame.Rect]] = [
            (GameMode.CLASSIC, "CLASSIC ENDLESS", pygame.Rect(WIDTH // 2 - 240, 160, 230, 48)),
            (GameMode.TIME_ATTACK, "TIME ATTACK (45s)", pygame.Rect(WIDTH // 2 + 10, 160, 230, 48)),
            (GameMode.MAZE_SURVIVAL, "MAZE SURVIVAL", pygame.Rect(WIDTH // 2 - 240, 220, 230, 48)),
            (GameMode.VERSUS_DUEL, "VERSUS DUEL (1v1)", pygame.Rect(WIDTH // 2 + 10, 220, 230, 48)),
        ]

        # Versus opponent toggle button
        self.versus_toggle_btn = pygame.Rect(WIDTH // 2 - 170, 280, 340, 40)

        # Speed level buttons
        self.level_buttons: list[pygame.Rect] = [
            pygame.Rect(40 + col * 72, 390, 60, 48) for col in range(10)
        ]

        # Start button
        self.start_button: pygame.Rect = pygame.Rect(WIDTH // 2 - 140, 495, 280, 54)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected_level = max(1, self.selected_level - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected_level = min(10, self.selected_level + 1)
            elif event.key == pygame.K_TAB:
                if self.selected_mode == GameMode.VERSUS_DUEL:
                    self.versus_is_ai = not self.versus_is_ai
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_game()
            elif event.key == pygame.K_m:
                midi_synth.toggle_mute()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_button.collidepoint(event.pos):
                self._start_game()
                return

            # Check mode buttons
            for mode, _, rect in self.mode_buttons:
                if rect.collidepoint(event.pos):
                    self.selected_mode = mode
                    return

            # Check Versus toggle
            if self.selected_mode == GameMode.VERSUS_DUEL and self.versus_toggle_btn.collidepoint(event.pos):
                self.versus_is_ai = not self.versus_is_ai
                return

            # Check speed level buttons
            for idx, rect in enumerate(self.level_buttons):
                if rect.collidepoint(event.pos):
                    self.selected_level = idx + 1

    def _start_game(self) -> None:
        midi_synth.start()
        pygame.time.set_timer(MIDI_MUSIC_EVENT, 420)

        if self.selected_mode == GameMode.VERSUS_DUEL:
            self.state_machine.change_state("versus", {"is_ai": self.versus_is_ai})
        else:
            self.state_machine.change_state(
                "play",
                {"mode": self.selected_mode, "level": self.selected_level},
            )

    def update(self, dt: float) -> None:
        self.pulse_frame += 1

    def draw(self, renderer: NeonRenderer) -> None:
        renderer.screen.fill(BACKGROUND)

        # Title
        renderer.draw_text("NEON SNAKE", renderer.title_font, CYAN, WIDTH // 2, 60)
        renderer.draw_text("CHOOSE GAME MODE", renderer.heading_font, WHITE, WIDTH // 2, 115)

        # Mode Buttons
        for mode, label, rect in self.mode_buttons:
            is_sel = mode == self.selected_mode
            renderer.draw_panel(rect, is_sel)
            color = BUTTON_TEXT if is_sel else WHITE
            renderer.draw_text(label, renderer.body_font, color, rect.centerx, rect.centery)

        # Versus Duel Sub-settings (AI vs Local P2)
        if self.selected_mode == GameMode.VERSUS_DUEL:
            opp_text = "OPPONENT: AGGRESSIVE AI BOT [Click to Toggle]" if self.versus_is_ai else "OPPONENT: LOCAL PLAYER 2 [Click to Toggle]"
            opp_color = AMBER if self.versus_is_ai else CYAN
            renderer.draw_panel(self.versus_toggle_btn, False)
            renderer.draw_text(opp_text, renderer.small_font, opp_color, self.versus_toggle_btn.centerx, self.versus_toggle_btn.centery)
        else:
            # Mode Description
            descriptions = {
                GameMode.CLASSIC: "Classic: Endless run with dynamic progressive arena morphing & portals.",
                GameMode.TIME_ATTACK: "Time Attack: 45s countdown timer. Every food eaten adds +3s to the clock.",
                GameMode.MAZE_SURVIVAL: "Maze Survival: Geometric neon labyrinth with deadly inner barriers.",
            }
            renderer.draw_text(descriptions[self.selected_mode], renderer.small_font, GRAY, WIDTH // 2, 290)

        # Speed Level Header & Buttons (for single player)
        if self.selected_mode != GameMode.VERSUS_DUEL:
            renderer.draw_text("Pacing & Speed", renderer.heading_font, WHITE, WIDTH // 2, 350)
            for idx, rect in enumerate(self.level_buttons):
                lvl = idx + 1
                is_selected = lvl == self.selected_level
                renderer.draw_panel(rect, is_selected)
                text_color = BUTTON_TEXT if is_selected else WHITE
                renderer.draw_text(str(lvl), renderer.body_font, text_color, rect.centerx, rect.centery)

            speed_names = ("Relaxed", "Easy", "Normal", "Fast", "Extreme")
            name_idx = min(4, (self.selected_level - 1) // 2)
            renderer.draw_text(f"Level {self.selected_level}  —  {speed_names[name_idx]} Speed", renderer.small_font, GOLD, WIDTH // 2, 455)
        else:
            renderer.draw_text("P1: WASD (Cyan)   vs   P2 / AI: Arrow Keys (Amber)", renderer.body_font, WHITE, WIDTH // 2, 380)
            renderer.draw_text("Best of 3 Rounds • Avoid opponent's tail & obstacles!", renderer.small_font, GOLD, WIDTH // 2, 420)

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
