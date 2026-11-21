"""High-performance renderer with pre-baked neon glow masks, HUD, and screen shake."""

import math
import random
import pygame

from src.config import (
    BACKGROUND,
    BUTTON_TEXT,
    CELL_SIZE,
    CYAN,
    DARK_GREEN,
    DARK_GRAY,
    FRUIT_SPECS,
    FruitType,
    GHOST_PURPLE,
    GOLD,
    GRAY,
    GRID_COLUMNS,
    GRID_ROWS,
    HEIGHT,
    ICE_BLUE,
    PANEL,
    PANEL_BORDER,
    RED,
    WHITE,
    WIDTH,
)
from src.entities.food import FoodManager, SpecialFruit
from src.entities.particles import ParticleSystem
from src.entities.snake import Snake


class NeonRenderer:
    """Handles all drawing routines, pre-rendered neon glow effects, and HUD elements."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen: pygame.Surface = screen

        # Pre-load typography (Pre-loaded once, never during render loop)
        self.title_font = self._get_font(56, bold=True)
        self.heading_font = self._get_font(30, bold=True)
        self.body_font = self._get_font(20, bold=True)
        self.small_font = self._get_font(15, bold=False)

        # Screen shake state
        self.shake_duration: float = 0.0
        self.shake_magnitude: float = 0.0
        self.shake_offset: tuple[int, int] = (0, 0)

        # Pre-bake glow halos for maximum 60 FPS performance
        self.glow_cache: dict[tuple[int, int, int], pygame.Surface] = {}
        for color in (CYAN, RED, GOLD, ICE_BLUE, GHOST_PURPLE, DARK_GREEN):
            self.glow_cache[color] = self._create_glow_surface(color, radius=24, max_alpha=75)

    def _get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        try:
            return pygame.font.SysFont("bahnschrift", size, bold=bold)
        except Exception:
            return pygame.font.SysFont("arial", size, bold=bold)

    def _create_glow_surface(self, color: tuple[int, int, int], radius: int, max_alpha: int) -> pygame.Surface:
        """Creates a smooth radial alpha surface cached for blitting."""
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(max_alpha * (1.0 - (r / radius) ** 0.8))
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        return surf

    def trigger_shake(self, magnitude: float = 6.0, duration: float = 0.25) -> None:
        """Triggers screen shake impulse on impact or game over."""
        self.shake_magnitude = magnitude
        self.shake_duration = duration

    def update_shake(self, dt: float) -> None:
        """Updates screen shake timers and generates random offset."""
        if self.shake_duration > 0.0:
            self.shake_duration -= dt
            offset_x = int(random.uniform(-self.shake_magnitude, self.shake_magnitude))
            offset_y = int(random.uniform(-self.shake_magnitude, self.shake_magnitude))
            self.shake_offset = (offset_x, offset_y)
        else:
            self.shake_offset = (0, 0)

    def draw_grid_lines(self) -> None:
        """Draws subtle neon grid lines."""
        ox, oy = self.shake_offset
        for col in range(GRID_COLUMNS + 1):
            x = col * CELL_SIZE + ox
            pygame.draw.line(self.screen, PANEL, (x, oy), (x, HEIGHT + oy), 1)
        for row in range(GRID_ROWS + 1):
            y = row * CELL_SIZE + oy
            pygame.draw.line(self.screen, PANEL, (ox, y), (WIDTH + ox, y), 1)

    def draw_snake(self, snake: Snake, pulse_frame: int) -> None:
        """Renders snake body, glowing head, and ghost effects."""
        ox, oy = self.shake_offset

        # Determine head color based on active power-ups
        if snake.is_ghost:
            head_color = GHOST_PURPLE
            body_color = (130, 60, 160)
        elif snake.is_frozen:
            head_color = ICE_BLUE
            body_color = (40, 120, 150)
        else:
            head_color = CYAN
            body_color = DARK_GREEN

        # Render body segments
        for idx, segment in enumerate(snake.segments):
            seg_x = segment[0] * CELL_SIZE + ox
            seg_y = segment[1] * CELL_SIZE + oy
            is_head = idx == len(snake.segments) - 1

            if is_head:
                # Draw head glow halo
                glow_surf = self.glow_cache.get(head_color)
                if glow_surf:
                    glow_rect = glow_surf.get_rect(
                        center=(seg_x + CELL_SIZE // 2, seg_y + CELL_SIZE // 2)
                    )
                    self.screen.blit(glow_surf, glow_rect)

                # Draw head rect
                pygame.draw.rect(
                    self.screen,
                    head_color,
                    pygame.Rect(seg_x + 2, seg_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                    border_radius=5,
                )
            else:
                # Draw body rect
                pygame.draw.rect(
                    self.screen,
                    body_color,
                    pygame.Rect(seg_x + 2, seg_y + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                    border_radius=4,
                )

    def draw_foods(self, food_mgr: FoodManager, pulse_frame: int) -> None:
        """Renders regular apple and special fruit with countdown ring and glow."""
        ox, oy = self.shake_offset

        # 1. Regular Apple
        reg_x = food_mgr.regular_food[0] * CELL_SIZE + ox
        reg_y = food_mgr.regular_food[1] * CELL_SIZE + oy
        reg_center = (reg_x + CELL_SIZE // 2, reg_y + CELL_SIZE // 2)

        glow_red = self.glow_cache.get(RED)
        if glow_red:
            self.screen.blit(glow_red, glow_red.get_rect(center=reg_center))

        pulse_offset = int(math.sin(pulse_frame * 0.1) * 1.5)
        pygame.draw.circle(self.screen, RED, reg_center, 7 + pulse_offset)

        # 2. Special Fruit (if active)
        if food_mgr.special_fruit:
            spec = food_mgr.special_fruit
            cfg = FRUIT_SPECS[spec.fruit_type]
            sp_x = spec.position[0] * CELL_SIZE + ox
            sp_y = spec.position[1] * CELL_SIZE + oy
            sp_center = (sp_x + CELL_SIZE // 2, sp_y + CELL_SIZE // 2)

            glow_spec = self.glow_cache.get(cfg.color)
            if glow_spec:
                self.screen.blit(glow_spec, glow_spec.get_rect(center=sp_center))

            # Draw fruit core
            pygame.draw.circle(self.screen, cfg.color, sp_center, 8 + pulse_offset)

            # Draw countdown arc/ring around the fruit
            ring_rect = pygame.Rect(sp_x - 3, sp_y - 3, CELL_SIZE + 6, CELL_SIZE + 6)
            sweep_angle = spec.progress * 2 * math.pi
            if sweep_angle > 0.05:
                pygame.draw.arc(
                    self.screen,
                    cfg.color,
                    ring_rect,
                    0,
                    sweep_angle,
                    2,
                )

    def draw_hud(
        self,
        score: int,
        high_score: int,
        level: int,
        snake: Snake,
        food_mgr: FoodManager,
        is_muted: bool,
    ) -> None:
        """Draws scores, active power-up badges, and controls."""
        # Top HUD Panel background
        hud_bg = pygame.Rect(0, 0, WIDTH, 54)
        pygame.draw.rect(self.screen, PANEL, hud_bg)
        pygame.draw.line(self.screen, PANEL_BORDER, (0, 54), (WIDTH, 54), 2)

        # Score & High Score
        self.draw_text(f"SCORE  {score}", self.body_font, WHITE, 90, 27)
        self.draw_text(f"BEST  {high_score}", self.body_font, GOLD, WIDTH // 2, 27)
        self.draw_text(f"LEVEL {level}", self.body_font, CYAN, WIDTH - 180, 27)

        # Sound Mute indicator
        mute_text = "MUTED (M)" if is_muted else "AUDIO ON (M)"
        mute_color = GRAY if is_muted else CYAN
        self.draw_text(mute_text, self.small_font, mute_color, WIDTH - 75, 27)

        # Active Power-up Badges on HUD
        badge_y = 74
        if snake.is_ghost:
            self.draw_badge(
                f"GHOST: {snake.ghost_timer:.1f}s",
                GHOST_PURPLE,
                110,
                badge_y,
            )
        if snake.is_frozen:
            self.draw_badge(
                f"FREEZE: {snake.freeze_timer:.1f}s",
                ICE_BLUE,
                245,
                badge_y,
            )
        if food_mgr.special_fruit:
            spec = food_mgr.special_fruit
            cfg = FRUIT_SPECS[spec.fruit_type]
            self.draw_badge(
                f"{cfg.name.upper()}: {spec.time_remaining:.1f}s",
                cfg.color,
                WIDTH - 140,
                badge_y,
            )

    def draw_badge(self, text: str, color: tuple[int, int, int], center_x: int, center_y: int) -> None:
        """Draws a rounded glowing HUD status pill."""
        surface = self.small_font.render(text, True, color)
        width = surface.get_width() + 18
        height = surface.get_height() + 8
        rect = pygame.Rect(center_x - width // 2, center_y - height // 2, width, height)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=6)
        pygame.draw.rect(self.screen, color, rect, width=1, border_radius=6)
        self.screen.blit(surface, (rect.x + 9, rect.y + 4))

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center_x: int,
        center_y: int,
    ) -> None:
        """Utility for centered text blitting."""
        surface = font.render(text, True, color)
        left = center_x - surface.get_width() // 2
        top = center_y - surface.get_height() // 2
        self.screen.blit(surface, (left, top))

    def draw_panel(self, rect: pygame.Rect, selected: bool = False) -> None:
        """Draws a themed UI panel or button."""
        color = CYAN if selected else PANEL
        border_color = WHITE if selected else PANEL_BORDER
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=8)
