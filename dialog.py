"""Dialog box overlay with typewriter text effect."""

import pygame

from config import WINDOW_SIZE, PALETTE


class DialogBox:
    def __init__(self):
        self.active = False
        self.event = None
        self.text_progress = 0
        self.char_timer = 0
        self.chars_per_tick = 0.5  # reveal speed
        self.choice_index = 0
        self.box_height = 56
        self._font: pygame.font.Font | None = None
        self._small_font: pygame.font.Font | None = None

    @property
    def font(self):
        if self._font is None:
            self._font = pygame.font.Font(None, 14)
        return self._font

    @property
    def small_font(self):
        if self._small_font is None:
            self._small_font = pygame.font.Font(None, 12)
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
        """Handle input for dialog. Returns True if dialog consumed the event."""
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if not self.is_showing_complete:
                    self.text_progress = len(self.event.text)
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
                elif self.event and not self.event.choices:
                    self.dismiss()
                return True

        return False

    def render(self, screen: pygame.Surface):
        if not self.active or not self.event:
            return

        # Background box
        box = pygame.Surface((WINDOW_SIZE, self.box_height), pygame.SRCALPHA)
        box.fill((10, 10, 30, 230))  # dark navy, mostly opaque
        screen.blit(box, (0, WINDOW_SIZE - self.box_height))

        # Title
        title_surf = self.small_font.render(
            self.event.title, True, (255, 215, 0)
        )
        screen.blit(title_surf, (6, WINDOW_SIZE - self.box_height + 4))

        # Text with word wrap (typewriter)
        visible = self.event.text[:self.text_progress]
        lines = visible.split('\n')
        y = WINDOW_SIZE - self.box_height + 18
        for line in lines:
            if not line:
                y += 14
                continue
            text_surf = self.font.render(line, True, (220, 220, 220))
            screen.blit(text_surf, (8, y))
            y += 14

        # Choices (shown when text fully revealed)
        if self.is_showing_complete and self.event.choices:
            y = WINDOW_SIZE - self.box_height + 18 + len(lines) * 14 + 4
            for i, (label, _) in enumerate(self.event.choices):
                prefix = ">" if i == self.choice_index else " "
                color = (255, 255, 255) if i == self.choice_index else (160, 160, 160)
                choice_surf = self.small_font.render(
                    f" {prefix} {label}", True, color
                )
                screen.blit(choice_surf, (8, y))
                y += 14
