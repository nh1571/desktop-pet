"""Renders 16x16 pixel grids to cached scaled pygame Surfaces."""

import pygame
from config import PALETTE, SPRITE_PIXEL_SIZE, SPRITE_SCALE


class SpriteRenderer:
    def __init__(self):
        self.palette = PALETTE
        self.sprite_size = SPRITE_PIXEL_SIZE
        self.scale = SPRITE_SCALE
        self.cache = {}

    def _cache_key(self, pixel_grid: list) -> tuple:
        return tuple(tuple(row) for row in pixel_grid)

    def render(self, pixel_grid: list) -> pygame.Surface:
        """Convert a 16x16 pixel grid to a cached scaled Surface."""
        key = self._cache_key(pixel_grid)
        if key in self.cache:
            return self.cache[key]

        surf = pygame.Surface(
            (self.sprite_size * self.scale, self.sprite_size * self.scale),
            pygame.SRCALPHA,
        )

        for y, row in enumerate(pixel_grid):
            for x, idx in enumerate(row):
                if idx == 0:
                    continue
                color = self.palette.get(idx, (0, 0, 0))
                rect = pygame.Rect(
                    x * self.scale,
                    y * self.scale,
                    self.scale,
                    self.scale,
                )
                pygame.draw.rect(surf, color, rect)

        self.cache[key] = surf
        return surf

    def clear_cache(self):
        self.cache.clear()
