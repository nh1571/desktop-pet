"""Food dropping and eating system — spawn food items that fall with physics."""

import random
import math
import pygame
import pygame.gfxdraw as gfx
from config import WINDOW_SIZE


# Food type definitions: (color, bonus_hunger, bonus_happiness, shape)
FOOD_TYPES = [
    {"name": "cookie", "color": (210, 160, 100), "hunger": 15, "happiness": 5,
     "shape": "circle", "size": 10},
    {"name": "apple", "color": (220, 60, 50), "hunger": 12, "happiness": 3,
     "shape": "circle", "size": 11},
    {"name": "candy", "color": (240, 120, 200), "hunger": 8, "happiness": 10,
     "shape": "diamond", "size": 10},
    {"name": "cake", "color": (255, 200, 100), "hunger": 20, "happiness": 8,
     "shape": "triangle", "size": 12},
    {"name": "cherry", "color": (200, 30, 50), "hunger": 10, "happiness": 7,
     "shape": "double", "size": 9},
    {"name": "star_candy", "color": (255, 220, 60), "hunger": 10, "happiness": 12,
     "shape": "star", "size": 12},
]


class FoodItem:
    def __init__(self, x, y, food_type: dict):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-3, -1)
        self.gravity = 0.15
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)
        self.food_type = food_type
        self.alive = True
        self.scale = 1.0
        self.bounce = 0.0

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed

        # Bounce off edges
        margin = 20
        if self.x < margin:
            self.x = margin
            self.vx *= -0.6
        elif self.x > WINDOW_SIZE - margin:
            self.x = WINDOW_SIZE - margin
            self.vx *= -0.6

        # Bounce off bottom (before disappearing)
        if self.y > WINDOW_SIZE - 30:
            self.y = WINDOW_SIZE - 30
            self.vy *= -0.5
            self.bounce = 4
            if abs(self.vy) < 0.5:
                self.alive = False

        # Bounce animation
        if self.bounce > 0:
            self.bounce *= 0.85
            if self.bounce < 0.1:
                self.bounce = 0

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y) - int(self.bounce)
        color = self.food_type["color"]
        size = int(self.food_type["size"] * self.scale)
        shape = self.food_type["shape"]

        item_surf = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)

        # Shadow
        gfx.filled_ellipse(item_surf, cx, cy + size, size, size // 3, (0, 0, 0, 30))

        if shape == "circle":
            self._draw_circle(item_surf, cx, cy, size, color)
        elif shape == "diamond":
            self._draw_diamond(item_surf, cx, cy, size, color)
        elif shape == "triangle":
            self._draw_triangle(item_surf, cx, cy, size, color)
        elif shape == "double":
            self._draw_double(item_surf, cx, cy, size, color)
        elif shape == "star":
            self._draw_star(item_surf, cx, cy, size, color)

        surf.blit(item_surf, (0, 0))

    def _draw_circle(self, surf, cx, cy, size, color):
        gfx.filled_circle(surf, cx, cy, size, color)
        gfx.aacircle(surf, cx, cy, size, (*color[:3], 150))
        # Highlight
        hl_r = max(2, size // 3)
        gfx.filled_circle(surf, cx - size // 3, cy - size // 3, hl_r,
                           (255, 255, 255, 150))

    def _draw_diamond(self, surf, cx, cy, size, color):
        pts = [
            (cx, cy - size),
            (cx + size, cy),
            (cx, cy + size),
            (cx - size, cy),
        ]
        pygame.draw.polygon(surf, color, pts)
        gfx.aapolygon(surf, pts, (*color[:3], 150))
        gfx.filled_circle(surf, cx - size // 3, cy - size // 3,
                          max(2, size // 3), (255, 255, 255, 150))

    def _draw_triangle(self, surf, cx, cy, size, color):
        pts = [
            (cx, cy - size),
            (cx + size, cy + size),
            (cx - size, cy + size),
        ]
        pygame.draw.polygon(surf, color, pts)
        gfx.aapolygon(surf, pts, (*color[:3], 150))

    def _draw_double(self, surf, cx, cy, size, color):
        # Two overlapping circles (cherry)
        offset = size // 2
        gfx.filled_circle(surf, cx - offset, cy, size, color)
        gfx.aacircle(surf, cx - offset, cy, size, (*color[:3], 150))
        gfx.filled_circle(surf, cx + offset, cy, size, (min(255, color[0] + 30),
                           min(255, color[1] + 10), min(255, color[2] + 10)))
        gfx.aacircle(surf, cx + offset, cy, size, (*color[:3], 150))
        # Stem
        pygame.draw.line(surf, (80, 150, 60), (cx, cy - size), (cx, cy - size - 6), 2)

    def _draw_star(self, surf, cx, cy, size, color):
        pts = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            r = size if i % 2 == 0 else size // 2
            pts.append((cx + int(r * math.cos(angle)), cy - int(r * math.sin(angle))))
        pygame.draw.polygon(surf, color, pts)
        gfx.aapolygon(surf, pts, (*color[:3], 150))
        gfx.filled_circle(surf, cx, cy, size // 3, (255, 255, 255, 130))


class FoodSystem:
    def __init__(self):
        self.items: list[FoodItem] = []

    @property
    def active_items(self):
        return self.items

    def spawn_random(self, count: int = 3):
        for _ in range(count):
            food_type = random.choice(FOOD_TYPES)
            x = random.randint(50, WINDOW_SIZE - 50)
            y = random.randint(-20, 30)
            self.items.append(FoodItem(x, y, food_type))

    def get_nearest_item(self, pet_cx):
        """Return position of nearest food item for eye tracking."""
        if not self.items:
            return None
        nearest = min(self.items, key=lambda f: abs(f.x - pet_cx))
        return (nearest.x, nearest.y)

    def update(self, slime, pet_pos) -> bool:
        """Update all items. Return True if any were eaten."""
        eaten = False
        px, py = pet_pos
        for item in self.items[:]:
            item.update()
            if not item.alive:
                self.items.remove(item)
                continue
            # Check collision with pet mouth area
            dist = math.hypot(item.x - px, item.y - py)
            if dist < 40:
                self.items.remove(item)
                eaten = True
        return eaten

    def draw(self, surf):
        for item in self.items:
            item.draw(surf)

    def clear(self):
        self.items.clear()
