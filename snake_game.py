import os
import random
import sys
from pathlib import Path

import pygame
import pygame.midi
os.environ["SDL_VIDEO_WINDOW_POS"] = "100,80"
pygame.init()
pygame.midi.init()
pygame.display.set_caption("Neon Snake")

WIDTH, HEIGHT = 800, 600
GRID_COLUMNS = 40
GRID_ROWS = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

CYAN = (77, 230, 255)
GREEN = (77, 255, 163)
DARK_GREEN = (20, 97, 64)
RED = (255, 92, 122)
GOLD = (255, 201, 87)
WHITE = (242, 250, 255)
PANEL = (26, 36, 69)
GRAY = (140, 153, 184)
BACKGROUND = (6, 10, 22)
BUTTON_TEXT = (8, 20, 31)

title_font = pygame.font.SysFont("bahnschrift", 58, bold=True)
heading_font = pygame.font.SysFont("bahnschrift", 32, bold=True)
body_font = pygame.font.SysFont("bahnschrift", 22)
small_font = pygame.font.SysFont("bahnschrift", 17)

HIGH_SCORE_FILE = Path(__file__).with_name("high_score.txt")


class MidiSynth:
    def __init__(self) -> None:
        self.output = None
        self.music_index = 0
        self.active_notes: set[int] = set()
        try:
            output_count = pygame.midi.get_count()
            for device_id in range(output_count):
                info = pygame.midi.get_device_info(device_id)
                if info and info[3] == 1:
                    self.output = pygame.midi.Output(device_id)
                    break
            if self.output:
                self.output.write_short(0xC0, 80)
        except pygame.midi.MidiException:
            self.output = None

    def note(self, pitch: int, duration_ms: int = 120, volume: int = 90) -> None:
        if self.output is None:
            return
        try:
            self.output.note_on(pitch, volume)
            self.active_notes.add(pitch)
            pygame.time.set_timer(MIDI_NOTE_OFF_EVENT, duration_ms, True)
        except pygame.midi.MidiException:
            self.output = None

    def eat(self) -> None:
        self.note(76, 180, 110)
        self.note(83, 180, 75)

    def death(self) -> None:
        if self.output:
            for pitch in (55, 53, 50):
                self.note(pitch, 380, 95)

    def start(self) -> None:
        self.note(64, 180, 85)

    def music_tick(self) -> None:
        if self.output is None:
            return
        melody = (60, 64, 67, 71, 67, 64, 62, 67)
        pitch = melody[self.music_index % len(melody)]
        self.note(pitch, 420, 45)
        if self.music_index % 4 == 0:
            bass = (36, 38, 36, 43)[(self.music_index // 4) % 4]
            self.note(bass, 650, 65)
        self.music_index += 1

    def release_notes(self) -> None:
        if self.output is None:
            return
        for pitch in tuple(self.active_notes):
            try:
                self.output.note_off(pitch, 0)
            except pygame.midi.MidiException:
                return
        self.active_notes.clear()

    def close(self) -> None:
        if self.output:
            try:
                self.release_notes()
                self.output.close()
            except pygame.midi.MidiException:
                pass


midi = MidiSynth()
MIDI_NOTE_OFF_EVENT = pygame.USEREVENT + 1
MIDI_MUSIC_EVENT = pygame.USEREVENT + 2


def load_high_score() -> int:
    try:
        return int(HIGH_SCORE_FILE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0


def save_high_score(score: int) -> None:
    try:
        HIGH_SCORE_FILE.write_text(str(score), encoding="utf-8")
    except OSError:
        pass


CELL_SIZE = 20


def world_position(column: int, row: int) -> tuple[int, int]:
    return column * CELL_SIZE, row * CELL_SIZE


def random_food(snake: list[list[int]]) -> list[int]:
    available = [
        [column, row]
        for column in range(GRID_COLUMNS)
        for row in range(GRID_ROWS)
        if [column, row] not in snake
    ]
    return random.choice(available)


def reset_game_state() -> tuple[
    int, int, int, int, list[list[int]], int, list[int]
]:
    snake = [[GRID_COLUMNS // 2, GRID_ROWS // 2]]
    food = random_food(snake)
    return snake[0][0], snake[0][1], 0, 0, snake, 1, food


def draw_world(snake: list[list[int]], food: list[int],
               direction: tuple[int, int], pulse: int) -> None:
    screen.fill(BACKGROUND)

    for column in range(GRID_COLUMNS + 1):
        pygame.draw.line(
            screen, PANEL,
            (column * CELL_SIZE, 0),
            (column * CELL_SIZE, HEIGHT),
            1,
        )
    for row in range(GRID_ROWS + 1):
        pygame.draw.line(
            screen, PANEL,
            (0, row * CELL_SIZE),
            (WIDTH, row * CELL_SIZE),
            1,
        )

    food_x, food_y = world_position(food[0], food[1])
    pygame.draw.circle(
        screen,
        RED,
        (food_x + CELL_SIZE // 2, food_y + CELL_SIZE // 2),
        7 + (pulse % 12) // 6,
    )

    for index, segment in enumerate(snake):
        x, y = world_position(segment[0], segment[1])
        if index == len(snake) - 1:
            color = CYAN
        else:
            color = DARK_GREEN
        pygame.draw.rect(
            screen,
            color,
            pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
            border_radius=5,
        )


def draw_screen_text(text: str, font: pygame.font.Font,
                     color: tuple[int, int, int],
                     center_x: int, center_y: int) -> None:
    surface = font.render(text, True, color)
    left = center_x - surface.get_width() // 2
    top = center_y - surface.get_height() // 2
    screen.blit(surface, (left, top))


def draw_screen_panel(rect: pygame.Rect, selected: bool = False) -> None:
    color = CYAN if selected else PANEL
    pygame.draw.rect(screen, color, rect, border_radius=8)


def draw_hud(score: int, high_score: int, level: int) -> None:
    draw_screen_text(f"SCORE  {score}", body_font, WHITE, 95, 28)
    draw_screen_text(f"BEST  {high_score}", body_font, GOLD, 705, 28)
    draw_screen_text(f"LEVEL {level}", small_font, CYAN, 720, 58)


def start_screen() -> int:
    selected_level = 5
    level_buttons = [
        pygame.Rect(40 + column * 70, 340, 58, 58)
        for column in range(10)
    ]
    start_button = pygame.Rect(WIDTH // 2 - 130, 470, 260, 64)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                midi.close()
                pygame.midi.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    midi.start()
                    pygame.time.set_timer(MIDI_MUSIC_EVENT, 420)
                    return selected_level
                for index, rect in enumerate(level_buttons):
                    if rect.collidepoint(event.pos):
                        selected_level = index + 1
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    midi.start()
                    pygame.time.set_timer(MIDI_MUSIC_EVENT, 420)
                    return selected_level

        screen.fill(BACKGROUND)

        draw_screen_text("NEON SNAKE", title_font, CYAN, WIDTH // 2, 95)
        draw_screen_text("Choose your speed", heading_font, WHITE, WIDTH // 2, 210)

        for index, rect in enumerate(level_buttons):
            level = index + 1
            draw_screen_panel(rect, level == selected_level)
            text_color = BUTTON_TEXT if level == selected_level else WHITE
            draw_screen_text(str(level), body_font, text_color, rect.centerx, rect.centery)

        speed_names = ("Relaxed", "Easy", "Normal", "Fast", "Extreme")
        name_index = min(4, (selected_level - 1) // 2)
        draw_screen_text(
            f"Level {selected_level}  -  {speed_names[name_index]}",
            body_font,
            GOLD,
            WIDTH // 2,
            420,
        )
        draw_screen_panel(start_button, True)
        draw_screen_text("START GAME", body_font, BUTTON_TEXT,
                         start_button.centerx, start_button.centery)
        draw_screen_text("Arrow keys or WASD  -  P or Esc to pause",
                         small_font, GRAY, WIDTH // 2, 555)

        pygame.display.flip()
        clock.tick(30)


def game_over_screen(score: int, high_score: int) -> bool:
    replay_button = pygame.Rect(WIDTH // 2 - 150, 390, 300, 58)
    quit_button = pygame.Rect(WIDTH // 2 - 150, 464, 300, 58)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                midi.close()
                pygame.midi.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_c, pygame.K_RETURN, pygame.K_SPACE):
                    return True
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if replay_button.collidepoint(event.pos):
                    return True
                if quit_button.collidepoint(event.pos):
                    return False
            if event.type == MIDI_NOTE_OFF_EVENT:
                midi.release_notes()

        screen.fill(BACKGROUND)
        draw_screen_text("GAME OVER", title_font, RED, WIDTH // 2, 180)
        draw_screen_text(f"Score: {score}", heading_font, WHITE, WIDTH // 2, 270)
        draw_screen_text(f"Best: {high_score}", body_font, GOLD, WIDTH // 2, 320)
        draw_screen_panel(replay_button, True)
        draw_screen_text("PLAY AGAIN", body_font, BUTTON_TEXT,
                         replay_button.centerx, replay_button.centery)
        draw_screen_panel(quit_button, False)
        draw_screen_text("QUIT", body_font, WHITE,
                         quit_button.centerx, quit_button.centery)
        pygame.display.flip()
        clock.tick(30)


def game_loop(speed_level: int) -> None:
    high_score = load_high_score()

    while True:
        (
            x,
            y,
            x_change,
            y_change,
            snake,
            snake_length,
            food,
        ) = reset_game_state()
        score = 0
        direction = (0, 0)
        paused = False
        pulse = 0
        game_over = False
        speed = 5 + (speed_level - 1) * 2

        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    midi.close()
                    pygame.midi.quit()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_p, pygame.K_ESCAPE):
                        paused = not paused
                    elif not paused:
                        if event.key in (pygame.K_LEFT, pygame.K_a) and x_change != 1:
                            x_change, y_change = -1, 0
                        elif event.key in (pygame.K_RIGHT, pygame.K_d) and x_change != -1:
                            x_change, y_change = 1, 0
                        elif event.key in (pygame.K_UP, pygame.K_w) and y_change != 1:
                            x_change, y_change = 0, -1
                        elif event.key in (pygame.K_DOWN, pygame.K_s) and y_change != -1:
                            x_change, y_change = 0, 1
                        direction = (x_change, y_change)
                if event.type == MIDI_NOTE_OFF_EVENT:
                    midi.release_notes()
                elif event.type == MIDI_MUSIC_EVENT:
                    if not paused:
                        midi.music_tick()

            if not paused:
                x += x_change
                y += y_change

                if x >= GRID_COLUMNS or x < 0 or y >= GRID_ROWS or y < 0:
                    game_over = True

                if not game_over:
                    head = [x, y]
                    snake.append(head)
                    if len(snake) > snake_length:
                        del snake[0]

                    if head in snake[:-1]:
                        game_over = True

                    if not game_over and x == food[0] and y == food[1]:
                        snake_length += 1
                        score += 10
                        high_score = max(high_score, score)
                        save_high_score(high_score)
                        food = random_food(snake)
                        speed = min(23, speed + 1)
                        midi.eat()

            draw_world(snake, food, direction, pulse)
            draw_hud(score, high_score, level=speed_level)

            if paused:
                draw_screen_text("PAUSED", title_font, CYAN, WIDTH // 2, HEIGHT // 2 - 25)
                draw_screen_text("Press P to continue", body_font, WHITE,
                                 WIDTH // 2, HEIGHT // 2 + 45)

            pygame.display.flip()
            pulse += 1
            clock.tick(speed)

        midi.death()
        if not game_over_screen(score, high_score):
            midi.close()
            pygame.midi.quit()
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    level = start_screen()
    game_loop(level)
