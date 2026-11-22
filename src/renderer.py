"""High-performance renderer with pre-baked neon glow masks, obstacles, portals, and HUDs."""

import math
import random
import pygame

from src.config import (
    AMBER,
    BACKGROUND,
    BUTTON_TEXT,
    CELL_SIZE,
    CYAN,
    DARK_AMBER,
    DARK_GRAY,
    DARK_GREEN,
    FRUIT_SPECS,
    FruitType,
    GHOST_PURPLE,
    GOLD,
    GRAY,
    GRID_COLUMNS,
    GRID_MIN_ROW,
    GRID_ROWS,
    HEIGHT,
    HUD_HEIGHT,
    ICE_BLUE,
    OBSTACLE_BORDER,
    OBSTACLE_COLOR,
    PANEL,
    PANEL_BORDER,
    PORTAL_BLUE,
    PORTAL_VIOLET,
    RED,
    WHITE,
    WIDTH,
)
from src.entities.food import FoodManager, SpecialFruit
from src.entities.obstacles import QuantumPortal
from src.entities.particles import ParticleSystem
from src.entities.snake import Snake


class NeonRenderer:
    """Handles all drawing routines, pre-rendered neon glow effects, and mode-specific HUDs."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen: pygame.Surface = screen

        # Pre-load typography
        self.title_font = self._get_font(56, bold=True)
        self.heading_font = self._get_font(26, bold=True)
        self.body_font = self._get_font(18, bold=True)
        self.small_font = self._get_font(14, bold=False)

        # Screen shake state
        self.shake_duration: float = 0.0
        self.shake_magnitude: float = 0.0
        self.shake_offset: tuple[int, int] = (0, 0)

        # Pre-bake glow halos for maximum 60 FPS performance
        self.glow_cache: dict[tuple[int, int, int], pygame.Surface] = {}
        cached_colors = (
            CYAN,
            RED,
            GOLD,
            ICE_BLUE,
            GHOST_PURPLE,
            DARK_GREEN,
            AMBER,
            DARK_AMBER,
            PORTAL_BLUE,
            PORTAL_VIOLET,
            OBSTACLE_BORDER,
        )
        for color in cached_colors:
            self.glow_cache[color] = self._create_glow_surface(color, radius=24, max_alpha=75)

    def _get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        try:
            return pygame.font.SysFont("bahnschrift", size, bold=bold)
        except Exception:
            return pygame.font.SysFont("arial", size, bold=bold)

    def _create_glow_surface(self, color: tuple[int, int, int], radius: int, max_alpha: int) -> pygame.Surface:
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(max_alpha * (1.0 - (r / radius) ** 0.8))
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        return surf

    def trigger_shake(self, magnitude: float = 6.0, duration: float = 0.25) -> None:
        self.shake_magnitude = magnitude
        self.shake_duration = duration

    def update_shake(self, dt: float) -> None:
        if self.shake_duration > 0.0:
            self.shake_duration -= dt
            ox = int(random.uniform(-self.shake_magnitude, self.shake_magnitude))
            oy = int(random.uniform(-self.shake_magnitude, self.shake_magnitude))
            self.shake_offset = (ox, oy)
        else:
            self.shake_offset = (0, 0)

    def draw_grid_lines(self) -> None:
        """Renders subtle neon grid lines strictly inside the playable arena."""
        ox, oy = self.shake_offset
        # Vertical grid lines
        for col in range(GRID_COLUMNS + 1):
            x = col * CELL_SIZE + ox
            pygame.draw.line(self.screen, PANEL, (x, HUD_HEIGHT + oy), (x, HEIGHT + oy), 1)
        # Horizontal grid lines
        for row in range(GRID_MIN_ROW, GRID_ROWS + 1):
            y = row * CELL_SIZE + oy
            pygame.draw.line(self.screen, PANEL, (ox, y), (WIDTH + ox, y), 1)

    def draw_obstacles(self, obstacles: set[tuple[int, int]]) -> None:
        """Renders neon barrier wall blocks."""
        ox, oy = self.shake_offset
        for col, row in obstacles:
            bx = col * CELL_SIZE + ox
            by = row * CELL_SIZE + oy
            rect = pygame.Rect(bx + 1, by + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect, border_radius=3)
            pygame.draw.rect(self.screen, OBSTACLE_BORDER, rect, width=1, border_radius=3)

    def draw_portals(self, portal: QuantumPortal | None, pulse_frame: int) -> None:
        """Renders paired spinning quantum vortex gates."""
        if not portal:
            return
        ox, oy = self.shake_offset
        gates = [(portal.gate_a, PORTAL_BLUE), (portal.gate_b, PORTAL_VIOLET)]

        for (col, row), color in gates:
            cx = col * CELL_SIZE + CELL_SIZE // 2 + ox
            cy = row * CELL_SIZE + CELL_SIZE // 2 + oy

            glow = self.glow_cache.get(color)
            if glow:
                self.screen.blit(glow, glow.get_rect(center=(cx, cy)))

            # Spinning vortex ring
            angle = (pulse_frame * 0.12) % (2 * math.pi)
            ring_rect = pygame.Rect(cx - 10, cy - 10, 20, 20)
            pygame.draw.arc(self.screen, color, ring_rect, angle, angle + math.pi * 1.5, 3)
            pygame.draw.circle(self.screen, WHITE, (cx, cy), 3)

    def draw_snake(self, snake: Snake, pulse_frame: int) -> None:
        """Renders snake body, glowing head, and eyes in movement direction."""
        ox, oy = self.shake_offset

        if snake.is_ghost:
            head_color = GHOST_PURPLE
            body_color = (130, 60, 160)
        elif snake.is_frozen:
            head_color = ICE_BLUE
            body_color = (40, 120, 150)
        else:
            head_color = snake.head_color
            body_color = snake.body_color

        for idx, segment in enumerate(snake.segments):
            seg_x = segment[0] * CELL_SIZE + ox
            seg_y = segment[1] * CELL_SIZE + oy
            is_head = idx == len(snake.segments) - 1

            if is_head:
                glow_surf = self.glow_cache.get(head_color)
                if glow_surf:
                    glow_rect = glow_surf.get_rect(center=(seg_x + CELL_SIZE // 2, seg_y + CELL_SIZE // 2))
                    self.screen.blit(glow_surf, glow_rect)

                pygame.draw.rect(
                    self.screen,
                    head_color,
                    pygame.Rect(seg_x + 2, seg_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                    border_radius=5,
                )

                # Snake eyes
                dx, dy = snake.current_direction
                cx = seg_x + CELL_SIZE // 2
                cy = seg_y + CELL_SIZE // 2
                eye_dist = 4
                if dx == 0 and dy == 0:
                    dx, dy = 1, 0

                px, py = -dy, dx
                e1_x = cx + dx * 4 + px * eye_dist
                e1_y = cy + dy * 4 + py * eye_dist
                e2_x = cx + dx * 4 - px * eye_dist
                e2_y = cy + dy * 4 - py * eye_dist

                pygame.draw.circle(self.screen, WHITE, (int(e1_x), int(e1_y)), 2)
                pygame.draw.circle(self.screen, WHITE, (int(e2_x), int(e2_y)), 2)
            else:
                pygame.draw.rect(
                    self.screen,
                    body_color,
                    pygame.Rect(seg_x + 2, seg_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                    border_radius=4,
                )

    def draw_foods(self, food_mgr: FoodManager, pulse_frame: int) -> None:
        ox, oy = self.shake_offset

        # Regular Apple
        reg_x = food_mgr.regular_food[0] * CELL_SIZE + ox
        reg_y = food_mgr.regular_food[1] * CELL_SIZE + oy
        reg_center = (reg_x + CELL_SIZE // 2, reg_y + CELL_SIZE // 2)

        glow_red = self.glow_cache.get(RED)
        if glow_red:
            self.screen.blit(glow_red, glow_red.get_rect(center=reg_center))

        pulse_offset = int(math.sin(pulse_frame * 0.1) * 1.5)
        pygame.draw.circle(self.screen, RED, reg_center, 7 + pulse_offset)

        # Special Fruit
        if food_mgr.special_fruit:
            spec = food_mgr.special_fruit
            cfg = FRUIT_SPECS[spec.fruit_type]
            sp_x = spec.position[0] * CELL_SIZE + ox
            sp_y = spec.position[1] * CELL_SIZE + oy
            sp_center = (sp_x + CELL_SIZE // 2, sp_y + CELL_SIZE // 2)

            glow_spec = self.glow_cache.get(cfg.color)
            if glow_spec:
                self.screen.blit(glow_spec, glow_spec.get_rect(center=sp_center))

            pygame.draw.circle(self.screen, cfg.color, sp_center, 8 + pulse_offset)

            ring_rect = pygame.Rect(sp_x - 3, sp_y - 3, CELL_SIZE + 6, CELL_SIZE + 6)
            sweep_angle = spec.progress * 2 * math.pi
            if sweep_angle > 0.05:
                pygame.draw.arc(self.screen, cfg.color, ring_rect, 0, sweep_angle, 2)

    def draw_hud(
        self,
        score: int,
        high_score: int,
        level: int,
        snake: Snake,
        food_mgr: FoodManager,
        is_muted: bool,
    ) -> None:
        """Draws top HUD cleanly inside y = 0..60px with power-up badges integrated."""
        hud_bg = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(self.screen, PANEL, hud_bg)
        pygame.draw.line(self.screen, CYAN, (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)

        # Left: Score & High Score
        self.draw_text(f"SCORE: {score}", self.body_font, WHITE, 80, 28)
        self.draw_text(f"BEST: {high_score}", self.body_font, GOLD, 195, 28)

        # Center: Active Power-up Badges (Contained strictly within HUD)
        badge_x = 340
        if snake.is_ghost:
            self.draw_badge(f"GHOST: {snake.ghost_timer:.1f}s", GHOST_PURPLE, badge_x, 28)
            badge_x += 130
        if snake.is_frozen:
            self.draw_badge(f"FREEZE: {snake.freeze_timer:.1f}s", ICE_BLUE, badge_x, 28)
            badge_x += 130
        if food_mgr.special_fruit:
            spec = food_mgr.special_fruit
            cfg = FRUIT_SPECS[spec.fruit_type]
            self.draw_badge(f"{cfg.name.upper()}: {spec.time_remaining:.1f}s", cfg.color, badge_x, 28)

        # Right: Level & Mute
        self.draw_text(f"LVL {level}", self.body_font, CYAN, WIDTH - 160, 28)
        mute_text = "MUTED (M)" if is_muted else "AUDIO (M)"
        self.draw_text(mute_text, self.small_font, GRAY if is_muted else CYAN, WIDTH - 75, 28)

    def draw_time_attack_hud(self, score: int, time_left: float, is_muted: bool) -> None:
        hud_bg = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(self.screen, PANEL, hud_bg)
        pygame.draw.line(self.screen, GOLD, (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)

        timer_color = RED if time_left <= 10.0 else GOLD
        self.draw_text(f"SCORE: {score}", self.body_font, WHITE, 100, 28)
        self.draw_text(f"TIME REMAINING: {time_left:.1f}s", self.heading_font, timer_color, WIDTH // 2, 28)

        mute_text = "MUTED (M)" if is_muted else "AUDIO (M)"
        self.draw_text(mute_text, self.small_font, GRAY if is_muted else CYAN, WIDTH - 75, 28)

    def draw_versus_hud(
        self,
        p1_score: int,
        p2_score: int,
        p1_rounds: int,
        p2_rounds: int,
        is_ai: bool,
        is_muted: bool,
    ) -> None:
        hud_bg = pygame.Rect(0, 0, WIDTH, HUD_HEIGHT)
        pygame.draw.rect(self.screen, PANEL, hud_bg)
        pygame.draw.line(self.screen, PANEL_BORDER, (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)

        # Player 1 Info (Cyan)
        self.draw_text(f"P1 (WASD): {p1_score} pts", self.body_font, CYAN, 130, 20)
        self.draw_text(f"Rounds: {p1_rounds}/2", self.small_font, WHITE, 130, 42)

        # Center Duel VS
        self.draw_text("VS", self.heading_font, WHITE, WIDTH // 2, 28)

        # Player 2 / AI Info (Amber)
        rival_label = "AI BOT (Arrows)" if is_ai else "P2 (Arrows)"
        self.draw_text(f"{rival_label}: {p2_score} pts", self.body_font, AMBER, WIDTH - 150, 20)
        self.draw_text(f"Rounds: {p2_rounds}/2", self.small_font, WHITE, WIDTH - 150, 42)

    def draw_badge(self, text: str, color: tuple[int, int, int], center_x: int, center_y: int) -> None:
        surface = self.small_font.render(text, True, color)
        width = surface.get_width() + 14
        height = surface.get_height() + 6
        rect = pygame.Rect(center_x - width // 2, center_y - height // 2, width, height)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=5)
        pygame.draw.rect(self.screen, color, rect, width=1, border_radius=5)
        self.screen.blit(surface, (rect.x + 7, rect.y + 3))

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center_x: int,
        center_y: int,
    ) -> None:
        surface = font.render(text, True, color)
        left = center_x - surface.get_width() // 2
        top = center_y - surface.get_height() // 2
        self.screen.blit(surface, (left, top))

    def draw_panel(self, rect: pygame.Rect, selected: bool = False) -> None:
        color = CYAN if selected else PANEL
        border_color = WHITE if selected else PANEL_BORDER
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=8)
