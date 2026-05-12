"""Smooth circular particle effects with easing."""

import random
import pygame
import pygame.gfxdraw as gfx

from config import VECTOR_PALETTE as P


class Particle:
    def __init__(self, x, y, vx, vy, life, color, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        t = self.life / self.max_life
        # Ease-out fade
        return int(255 * t * t)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # subtle gravity
        self.life -= 1

    def draw(self, screen, offset=(0, 0)):
        ox, oy = offset
        px = int(self.x + ox)
        py = int(self.y + oy)
        r = max(1, self.size)
        alpha = self.alpha
        if alpha < 5:
            return
        color = (*self.color[:3], alpha)
        gfx.filled_circle(screen, px, py, r, color)
        gfx.aacircle(screen, px, py, r, color)


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, x, y, count=5, color=(255, 230, 100), spread=2, life_range=(15, 30),
             size_range=(2, 4)):
        for _ in range(count):
            vx = random.uniform(-spread, spread)
            vy = random.uniform(-spread - 1, 0)
            life = random.randint(*life_range)
            size = random.randint(*size_range)
            self.particles.append(Particle(x, y, vx, vy, life, color, size))

    def emit_sparkles(self, x, y, count=6):
        """Gold sparkles for happy state."""
        self.emit(x, y, count=count, color=P["sparkle"], spread=3,
                  life_range=(15, 35), size_range=(2, 5))

    def emit_hearts(self, x, y):
        """Small pink particles for eating/loved state."""
        self.emit(x, y, count=5, color=P["blush"][:3], spread=2,
                  life_range=(20, 40), size_range=(2, 4))

    def emit_tears(self, x, y):
        """Blue tear drops for sad state."""
        self.emit(x, y, count=3, color=P["tear"], spread=1,
                  life_range=(30, 60), size_range=(3, 5))

    def emit_z(self, x, y):
        """White 'Z' particles for sleeping state."""
        self.emit(x, y, count=1, color=(255, 255, 255), spread=0,
                  life_range=(40, 70), size_range=(4, 6))

    def emit_bubbles(self, x, y, count=4):
        """Floating bubbles for idle/curious state."""
        self.emit(x, y, count=count, color=(200, 230, 255),
                  spread=1.5, life_range=(30, 60), size_range=(3, 7))

    def emit_rainbow(self, x, y, count=8):
        """Rainbow burst for celebration."""
        colors = [
            (255, 100, 100), (255, 200, 60), (255, 255, 100),
            (100, 255, 100), (100, 180, 255), (130, 100, 255),
            (255, 120, 220),
        ]
        for i in range(count):
            color = colors[i % len(colors)]
            vx = random.uniform(-4, 4)
            vy = random.uniform(-5, -1)
            life = random.randint(20, 40)
            self.particles.append(Particle(x, y, vx, vy, life, color,
                                           random.randint(3, 6)))

    def emit_notes(self, x, y, count=3):
        """Musical note particles for dancing state."""
        note_colors = [(255, 220, 60), (255, 160, 60), (255, 100, 180)]
        for i in range(count):
            color = note_colors[i % len(note_colors)]
            vx = random.uniform(-2, 2)
            vy = random.uniform(-3, -0.5)
            life = random.randint(25, 50)
            self.particles.append(Particle(x, y, vx, vy, life, color,
                                           random.randint(4, 7)))

    def emit_trail(self, x, y, color=(120, 210, 120)):
        """Small trailing dots for movement."""
        self.emit(x, y, count=1, color=color, spread=0.5,
                  life_range=(8, 15), size_range=(2, 3))

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
