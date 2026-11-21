"""Particle system for 60 FPS neon sparks and explosion effects."""

import math
import random
import pygame

from src.config import CELL_SIZE, CYAN, RED


class Particle:
    """Individual visual particle with velocity, decay, and size."""

    __slots__ = ("x", "y", "vx", "vy", "color", "lifetime", "max_lifetime", "size")

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        lifetime: float,
        size: float,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self, dt: float) -> bool:
        """Updates particle position and lifetime. Returns False when dead."""
        self.x += self.vx * (dt * 60.0)
        self.y += self.vy * (dt * 60.0)
        self.vx *= 0.94
        self.vy *= 0.94
        self.lifetime -= dt
        return self.lifetime > 0.0


class ParticleSystem:
    """Manages spawning, updating, and drawing of all active particles."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def clear(self) -> None:
        """Removes all active particles."""
        self.particles.clear()

    def emit_burst(
        self,
        center_x: float,
        center_y: float,
        color: tuple[int, int, int],
        count: int = 18,
        speed_min: float = 1.5,
        speed_max: float = 4.5,
    ) -> None:
        """Emits an outward radial burst of glowing particles."""
        for _ in range(count):
            angle = random.uniform(0.0, 2.0 * math.pi)
            speed = random.uniform(speed_min, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.35, 0.7)
            size = random.uniform(2.5, 4.5)
            self.particles.append(Particle(center_x, center_y, vx, vy, color, lifetime, size))

    def emit_death_shards(self, segments: list[list[int]], head_color: tuple[int, int, int] = CYAN) -> None:
        """Emits an explosion of particles along the snake body on game over."""
        for col, row in segments:
            cx = col * CELL_SIZE + CELL_SIZE // 2
            cy = row * CELL_SIZE + CELL_SIZE // 2
            self.emit_burst(cx, cy, head_color, count=8, speed_min=2.0, speed_max=6.0)

    def update(self, dt: float) -> None:
        """Updates all living particles and purges dead ones."""
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface) -> None:
        """Renders particles with size decay."""
        for p in self.particles:
            alpha_ratio = max(0.0, p.lifetime / p.max_lifetime)
            current_size = max(1.0, p.size * alpha_ratio)
            radius = int(current_size)
            pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), radius)
