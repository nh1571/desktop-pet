"""Simple particle effects for sparkles, hearts, etc."""

import random
import pygame

from config import PALETTE


class Particle:
    def __init__(self, x, y, vx, vy, life, color_idx, size=2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color_idx = color_idx
        self.size = size

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        return int(255 * self.life / self.max_life)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity (subtle)
        self.life -= 1

    def draw(self, screen, offset=(0, 0)):
        color = PALETTE.get(self.color_idx, (255, 255, 255))
        ox, oy = offset
        rect = pygame.Rect(
            int(self.x + ox), int(self.y + oy),
            self.size, self.size
        )
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        surf.fill((*color, self.alpha))
        screen.blit(surf, rect)


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, x, y, count=5, color_idx=7, spread=2, life_range=(10, 30)):
        for _ in range(count):
            vx = random.uniform(-spread, spread)
            vy = random.uniform(-spread - 1, 0)  # upward bias
            life = random.randint(*life_range)
            size = random.randint(1, 3)
            self.particles.append(Particle(x, y, vx, vy, life, color_idx, size))

    def emit_sparkles(self, x, y):
        """Gold sparkles for happy state."""
        self.emit(x, y, count=6, color_idx=7, spread=3, life_range=(15, 35))

    def emit_hearts(self, x, y):
        """Small red particles for loved state."""
        self.emit(x, y, count=4, color_idx=6, spread=2, life_range=(20, 40))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if not p.alive:
                self.particles.remove(p)

    def draw(self, screen, offset=(0, 0)):
        for p in self.particles:
            p.draw(screen, offset)

    def clear(self):
        self.particles.clear()
