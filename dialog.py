"""Speech bubble dialog overlay with typewriter effect."""

import pygame
import pygame.gfxdraw as gfx

from config import WINDOW_SIZE


class DialogBox:
    def __init__(self):
        self.active = False
        self.event = None
        self.text_progress = 0
        self.char_timer = 0
        self.chars_per_tick = 0.6
        self.choice_index = 0
        self.on_choice = None
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None

    @property
    def font(self):
        if self._font is None:
            self._font = pygame.font.Font(None, 17)
        return self._font

    @property
    def small_font(self):
        if self._small_font is None:
            self._small_font = pygame.font.Font(None, 14)
        return self._small_font

    def show(self, event):
        self.active = True
        self.event = event
        self.text_progress = 0
        self.char_timer = 0
        self.choice_index = 0

    def dismiss(self):
        self.active = False
        self.event = None

    @property
    def is_showing_complete(self):
        if not self.event:
            return True
        return self.text_progress >= len(self.event.text)

    def update(self):
        if not self.active or not self.event:
            return
        self.char_timer += self.chars_per_tick
        full_len = len(self.event.text)
        while self.char_timer >= 1.0 and self.text_progress < full_len:
            self.text_progress += 1
            self.char_timer -= 1.0

    def handle_input(self, event) -> bool:
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if not self.is_showing_complete:
                    self.text_progress = len(self.event.text)
                elif self.event and self.event.choices:
                    _, outcome_id = self.event.choices[self.choice_index]
                    if self.on_choice:
                        self.on_choice(outcome_id)
                elif self.event and not self.event.choices:
                    self.dismiss()
                return True
            elif event.key == pygame.K_DOWN:
                if self.event and self.event.choices:
                    self.choice_index = (self.choice_index + 1) % len(self.event.choices)
                return True
            elif event.key == pygame.K_UP:
                if self.event and self.event.choices:
                    self.choice_index = (self.choice_index - 1) % len(self.event.choices)
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not self.is_showing_complete:
                    self.text_progress = len(self.event.text)
                elif self.event and self.event.choices:
                    _, outcome_id = self.event.choices[self.choice_index]
                    if self.on_choice:
                        self.on_choice(outcome_id)
                elif self.event and not self.event.choices:
                    self.dismiss()
                return True

        return False

    def render(self, screen: pygame.Surface):
        if not self.active or not self.event:
            return

        # Measure text to determine bubble size
        visible = self.event.text[:self.text_progress]
        lines = visible.split('\n')
        line_surfs = [self.font.render(line, True, (40, 40, 40))
                      for line in lines]
        max_w = max((s.get_width() for s in line_surfs), default=100)
        text_h = sum(s.get_height() + 2 for s in line_surfs)
        title_surf = self.small_font.render(self.event.title, True, (100, 100, 100))

        # Bubble dimensions
        pad = 14
        bubble_w = max(max_w, title_surf.get_width()) + pad * 2
        bubble_h = title_surf.get_height() + text_h + pad * 2 + 8

        # Extra for choices
        choice_h = 0
        if self.is_showing_complete and self.event.choices:
            choice_h = len(self.event.choices) * 18 + 8

        total_h = bubble_h + choice_h

        # Position bubble above the slime (center of window is slime, bubble above)
        bubble_x = (WINDOW_SIZE - bubble_w) // 2
        bubble_y = WINDOW_SIZE - total_h - 30

        # Draw bubble background — rounded rect
        bubble_surf = pygame.Surface((bubble_w + 4, total_h + 4), pygame.SRCALPHA)
        bubble_rect = pygame.Rect(2, 2, bubble_w, total_h)

        # Rounded rectangle approximation using overlapping shapes
        r = 10  # corner radius
        bg_color = (255, 255, 255, 235)
        outline_color = (180, 200, 180, 200)

        # Fill main area
        inner_rect = pygame.Rect(bubble_rect.x + r, bubble_rect.y,
                                  bubble_rect.w - 2 * r, bubble_rect.h)
        inner_rect2 = pygame.Rect(bubble_rect.x, bubble_rect.y + r,
                                   bubble_rect.w, bubble_rect.h - 2 * r)
        pygame.draw.rect(bubble_surf, bg_color, inner_rect)
        pygame.draw.rect(bubble_surf, bg_color, inner_rect2)

        # Corner circles
        for cx, cy in [(bubble_rect.x + r, bubble_rect.y + r),
                       (bubble_rect.x + bubble_rect.w - r, bubble_rect.y + r),
                       (bubble_rect.x + r, bubble_rect.y + bubble_rect.h - r),
                       (bubble_rect.x + bubble_rect.w - r, bubble_rect.y + bubble_rect.h - r)]:
            gfx.filled_circle(bubble_surf, cx, cy, r, bg_color)
            gfx.aacircle(bubble_surf, cx, cy, r, outline_color)

        # Outline
        pygame.draw.rect(bubble_surf, outline_color, inner_rect, 1)
        pygame.draw.rect(bubble_surf, outline_color, inner_rect2, 1)

        # Small triangle pointer at bottom
        tri_points = [
            (bubble_w // 2 - 6, total_h + 2),
            (bubble_w // 2 + 6, total_h + 2),
            (bubble_w // 2, total_h + 10),
        ]
        pygame.draw.polygon(bubble_surf, (255, 255, 255, 235), tri_points)
        gfx.aapolygon(bubble_surf, tri_points, outline_color)

        screen.blit(bubble_surf, (bubble_x - 2, bubble_y - 2))

        # Title
        screen.blit(title_surf, (bubble_x + pad, bubble_y + pad))

        # Text
        y = bubble_y + pad + title_surf.get_height() + 6
        for surf in line_surfs:
            screen.blit(surf, (bubble_x + pad, y))
            y += surf.get_height() + 2

        # Choices
        if self.is_showing_complete and self.event.choices:
            y = bubble_y + bubble_h + 4
            for i, (label, _) in enumerate(self.event.choices):
                is_sel = i == self.choice_index
                choice_color = (60, 120, 60) if is_sel else (140, 140, 140)
                prefix = "> " if is_sel else "  "
                choice_surf = self.small_font.render(f"{prefix}{label}", True,
                                                      choice_color)
                screen.blit(choice_surf, (bubble_x + pad + 4, y))
                y += 18
