"""Mini-game: catch falling food items by moving the slime with your mouse."""

import random
import math
import pygame
import pygame.gfxdraw as gfx
from config import WINDOW_SIZE
from food_system import FOOD_TYPES


class FallingItem:
    def __init__(self, x, y, food_type, speed):
        self.x = x
        self.y = y
        self.food_type = food_type
        self.speed = speed
        self.size = food_type["size"]
        self.color = food_type["color"]
        self.alive = True
        self.wobble = 0.0

    def update(self, dt):
        self.y += self.speed * dt * 60
        self.wobble += dt * 8
        if self.y > WINDOW_SIZE + 20:
            self.alive = False

    def draw(self, surf):
        cx = int(self.x + math.sin(self.wobble) * 3)
        cy = int(self.y)
        size = self.size
        color = self.color

        gfx.filled_circle(surf, cx, cy, size, color)
        gfx.aacircle(surf, cx, cy, size, (*color[:3], 150))
        hl_r = max(2, size // 3)
        gfx.filled_circle(surf, cx - size // 3, cy - size // 3, hl_r,
                           (255, 255, 255, 150))


class MiniGame:
    DURATION = 30.0  # seconds
    MAX_LIVES = 5

    def __init__(self):
        self.score = 0
        self.lives = self.MAX_LIVES
        self.time_left = 0.0
        self.is_finished = False
        self.is_active = False
        self.items: list[FallingItem] = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.6
        self.difficulty = 1.0

    def start(self):
        self.score = 0
        self.lives = self.MAX_LIVES
        self.time_left = self.DURATION
        self.is_finished = False
        self.is_active = True
        self.items.clear()
        self.spawn_timer = 0.0
        self.spawn_interval = 0.6
        self.difficulty = 1.0

    def update(self, dt, slime):
        if not self.is_active:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.is_finished = True
            self.is_active = False
            return

        # Difficulty ramp up
        elapsed = self.DURATION - self.time_left
        self.difficulty = 1.0 + elapsed / 15.0
        self.spawn_interval = max(0.25, 0.6 - elapsed * 0.015)

        # Spawn items
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            self._spawn_item()

        # Get slime position from mouse X (slime controlled by mouse x)
        mx = pygame.mouse.get_pos()[0]
        pet_x = max(30, min(WINDOW_SIZE - 30, mx))
        pet_y = WINDOW_SIZE // 2 + 15

        # Update slime position for catching
        slime.set_look_target(0, -50)

        # Update items
        for item in self.items[:]:
            item.update(dt)
            if not item.alive:
                self.items.remove(item)
                self.lives -= 1
                if self.lives <= 0:
                    self.is_finished = True
                    self.is_active = False
                continue
            # Check catch: item near pet
            dist = math.hypot(item.x - pet_x, item.y - pet_y)
            if dist < 45:
                self.items.remove(item)
                self.score += 10
                break

    def _spawn_item(self):
        food_type = random.choice(FOOD_TYPES[:4])  # simpler foods
        x = random.randint(30, WINDOW_SIZE - 30)
        speed = random.uniform(2.0, 3.5) * self.difficulty
        self.items.append(FallingItem(x, -20, food_type, speed))

    def draw(self, surf):
        if not self.is_active and not self.is_finished:
            return

        # Draw items
        for item in self.items:
            item.draw(surf)

        # HUD
        font = pygame.font.Font(None, 20)
        # Score
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        score_shadow = font.render(f"Score: {self.score}", True, (0, 0, 0))
        self._draw_with_shadow(surf, score_shadow, score_text, 10, 8)

        # Lives
        hearts = "♥" * self.lives + "♡" * (self.MAX_LIVES - self.lives)
        life_text = font.render(hearts, True, (255, 100, 100))
        life_shadow = font.render(hearts, True, (0, 0, 0))
        self._draw_with_shadow(surf, life_shadow, life_text, 10, 28)

        # Timer
        timer_text = font.render(f"Time: {self.time_left:.1f}s", True, (255, 255, 200))
        timer_shadow = font.render(f"Time: {self.time_left:.1f}s", True, (0, 0, 0))
        self._draw_with_shadow(surf, timer_shadow, timer_text,
                              WINDOW_SIZE - 120, 8)

    def _draw_with_shadow(self, surf, shadow, text, x, y):
        surf.blit(shadow, (x + 1, y + 1))
        surf.blit(text, (x, y))
