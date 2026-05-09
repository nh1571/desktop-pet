#!/usr/bin/env python3
"""Desktop Pet — Pixel Art Retro Companion. Entry point."""

import sys
import time

import pygame
import pygame._sdl2 as sdl2

from config import WINDOW_SIZE, DEFAULT_OPACITY, TARGET_FPS, PALETTE, AUTOSAVE_INTERVAL
from sprite_renderer import SpriteRenderer
from animation import AnimPlayer
from pet import Pet
from window_manager import WindowManager
from event_system import EventSystem
from dialog import DialogBox
from particles import ParticleSystem


class DesktopPetApp:
    def __init__(self, fast_mode=False):
        self.fast_mode = fast_mode
        self.speed = 60.0 if fast_mode else 1.0

        # Window
        self.screen = None
        self.wm = WindowManager()

        # Rendering
        self.renderer = SpriteRenderer()
        self.anim_player = AnimPlayer(self.renderer)

        # Pet
        self.pet = Pet(self.renderer, self.anim_player)

        # Event system
        self.event_system = EventSystem()
        self.dialog = DialogBox()
        self.particles = ParticleSystem()

        # UI state
        self.dragging = False
        self.drag_offset = (0, 0)
        self.always_on_top = False
        self.status_text: str | None = None
        self.status_timer = 0
        self.last_save = time.time()

        # Clock
        self.clock = pygame.time.Clock()

    def run(self):
        self._init_window()
        self._try_load()
        # Start idle animation
        self.pet._play_anim("idle")
        self._main_loop()

    def _init_window(self):
        # Get screen size before pygame takes over NSApplication
        import ctypes
        import ctypes.util
        cg = ctypes.CDLL(ctypes.util.find_library('CoreGraphics'))
        cg.CGMainDisplayID.restype = ctypes.c_uint32
        cg.CGDisplayPixelsWide.argtypes = [ctypes.c_uint32]
        cg.CGDisplayPixelsWide.restype = ctypes.c_size_t
        cg.CGDisplayPixelsHigh.argtypes = [ctypes.c_uint32]
        cg.CGDisplayPixelsHigh.restype = ctypes.c_size_t
        did = cg.CGMainDisplayID()
        sw = cg.CGDisplayPixelsWide(did)
        sh = cg.CGDisplayPixelsHigh(did)

        pygame.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_SIZE, WINDOW_SIZE), pygame.NOFRAME
        )
        self.screen.set_colorkey(PALETTE[0])
        pygame.display.set_caption("Desktop Pet")

        self.wm.init()
        win = sdl2.Window.from_display_module()
        self.wm.bind(win)
        self.wm.set_opacity(DEFAULT_OPACITY)

        # Position at bottom-right corner
        self.wm.set_position(sw - WINDOW_SIZE - 40, sh - WINDOW_SIZE - 80)

    def _try_load(self):
        from save_manager import SaveManager
        sm = SaveManager()
        data = sm.load()
        if data:
            self.pet.restore_from_dict(data)
            pos = data.get("position")
            if pos:
                self.wm.set_position(*pos)

    def _main_loop(self):
        running = True

        while running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Dialog handles input first if active
                elif self.dialog.active:
                    self.dialog.handle_input(event)

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
                    elif event.key == pygame.K_f:
                        self._handle_action("feed")
                    elif event.key == pygame.K_p:
                        self._handle_action("play")
                    elif event.key == pygame.K_t:
                        self._handle_action("talk")
                    elif event.key == pygame.K_s:
                        self._handle_action("sleep")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                        mx, my = pygame.mouse.get_pos()
                        wx, wy = self.wm.get_position()
                        self.drag_offset = (mx, my)
                    elif event.button == 3:
                        self._show_context_menu(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.drag_offset[0]
                        dy = event.pos[1] - self.drag_offset[1]
                        wx, wy = self.wm.get_position()
                        self.wm.set_position(wx + dx, wy + dy)

            # Update
            if self.dialog.active:
                self.dialog.update()
            else:
                prev_state = self.pet.state_machine.state
                self.pet.update(self.speed)
                new_state = self.pet.state_machine.state

                # Emit particles on state transitions
                if new_state != prev_state:
                    if new_state.name == "HAPPY":
                        self.particles.emit_sparkles(WINDOW_SIZE // 2, WINDOW_SIZE // 2 - 20)
                    elif new_state.name == "EATING":
                        self.particles.emit_hearts(WINDOW_SIZE // 2, WINDOW_SIZE // 2)

                # Check for story events
                ev = self.event_system.check_triggers(self.pet)
                if ev:
                    self.dialog.show(ev)

            # Update particles
            self.particles.update()

            # Update status display timer
            if self.status_text and self.status_timer > 0:
                self.status_timer -= 1

            # Autosave
            now = time.time()
            if now - self.last_save > AUTOSAVE_INTERVAL:
                self._save()
                self.last_save = now

            # Render
            self._render()

        # Cleanup
        self._save()
        self.wm._win.destroy()
        pygame.display.quit()
        pygame.quit()

    def _handle_action(self, action: str):
        if action == "quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        if action == "toggle_top":
            self.always_on_top = not getattr(self, 'always_on_top', False)
            self.wm.set_always_on_top(self.always_on_top)
            self.status_text = f"Always on top: {'ON' if self.always_on_top else 'OFF'}"
            self.status_timer = TARGET_FPS * 2
            return
        response = self.pet.interact(action)
        if response:
            self.status_text = response
            self.status_timer = TARGET_FPS * 3  # 3 seconds

    def _show_context_menu(self, pos):
        from context_menu import show_menu
        show_menu(pos, self._handle_action)

    def _render(self):
        self.screen.fill(PALETTE[0])

        pet_surf = self.anim_player.get_surface()
        if pet_surf:
            x = (WINDOW_SIZE - pet_surf.get_width()) // 2
            y = (WINDOW_SIZE - pet_surf.get_height()) // 2
            self.screen.blit(pet_surf, (x, y))

        # Particles
        self.particles.draw(self.screen, (x, y))

        # Dialog overlay (bottom of window)
        if self.dialog.active:
            self.dialog.render(self.screen)

        # Status text overlay (top of window)
        if self.status_text and self.status_timer > 0:
            self._render_status_text()

        pygame.display.flip()

    def _render_status_text(self):
        """Render a simple text bubble at the top."""
        font = pygame.font.Font(None, 14)
        lines = self.status_text.split('\n')
        y_offset = 4
        for line in lines:
            text_surf = font.render(line, True, (255, 255, 255))
            text_bg = pygame.Surface((text_surf.get_width() + 8, text_surf.get_height() + 4))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(180)
            self.screen.blit(text_bg, (4, y_offset))
            self.screen.blit(text_surf, (8, y_offset + 2))
            y_offset += text_surf.get_height() + 2

    def _save(self):
        from save_manager import SaveManager
        data = self.pet.to_dict()
        data["position"] = list(self.wm.get_position())
        sm = SaveManager()
        sm.save(data)


def main():
    fast = "--fast" in sys.argv
    app = DesktopPetApp(fast_mode=fast)
    app.run()


if __name__ == "__main__":
    main()
