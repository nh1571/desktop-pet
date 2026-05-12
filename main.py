#!/usr/bin/env python3
"""Desktop Pet — Q-style Vector Companion. Entry point."""

import sys
import time
import random

import pygame
import pygame._sdl2 as sdl2

from config import (WINDOW_SIZE, DEFAULT_OPACITY, TARGET_FPS,
                    VECTOR_PALETTE as P, AUTOSAVE_INTERVAL, STAGE_NAMES,
                    STAGE_SCALES)
from vector_renderer import VectorSlime
from vector_animation import AnimController, get_anim
from pet import Pet, PetState
from state_machine import StateMachine
from window_manager import WindowManager
from event_system import EventSystem
from dialog import DialogBox
from particles import ParticleSystem
from audio import SoundManager
from save_manager import SaveManager, ConfigManager


class DesktopPetApp:
    def __init__(self, fast_mode=False):
        self.fast_mode = fast_mode
        self.speed = 60.0 if fast_mode else 1.0

        # Window
        self.screen = None
        self.wm = WindowManager()

        # Vector rendering
        self.slime = VectorSlime()
        self.anim_ctrl = AnimController()

        # Pet logic (still manages needs, state machine, growth)
        self.pet = Pet(window_manager=self.wm,
                       screen_size=(1920, 1080))

        # Event system
        self.event_system = EventSystem()
        self.dialog = DialogBox()
        self.dialog.on_choice = self._on_dialog_choice
        self.particles = ParticleSystem()
        self.sound = SoundManager()
        self.config = ConfigManager()

        # UI state
        self.dragging = False
        self.drag_offset = (0, 0)
        self.always_on_top = False
        self.status_text: str | None = None
        self.status_timer = 0
        self.last_save = time.time()
        self.last_blink = time.time()
        self.next_blink = random.uniform(2.0, 5.0)

        # Clock
        self.clock = pygame.time.Clock()

    def run(self):
        self._init_window()
        self._try_load()
        self._play_anim("idle")
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
        self.sound.init()
        self.screen = pygame.display.set_mode(
            (WINDOW_SIZE, WINDOW_SIZE), pygame.NOFRAME | pygame.SRCALPHA
        )
        pygame.display.set_caption("Desktop Pet")

        self.wm.init()
        win = sdl2.Window.from_display_module()
        self.wm.bind(win)
        self.wm.set_opacity(DEFAULT_OPACITY)

        # Position at bottom-right corner
        self.wm.set_position(sw - WINDOW_SIZE - 40, sh - WINDOW_SIZE - 100)
        self.pet.screen_size = (sw, sh)

        # Load and apply config
        cfg = self.config.load()
        self.wm.set_opacity(cfg.get("opacity", 0.95))
        self.sound.set_volume(cfg.get("volume", 0.3))
        self.sound.muted = cfg.get("muted", False)
        self.pet.name = cfg.get("pet_name", "Slimy")
        if cfg.get("always_on_top", False):
            self.always_on_top = True
            self.wm.set_always_on_top(True)

    def _try_load(self):
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

                # Growth celebration
                if self.pet.just_grew_up:
                    self.particles.emit_sparkles(WINDOW_SIZE // 2,
                                                 WINDOW_SIZE // 2 - 40, count=16)
                    stage_name = STAGE_NAMES.get(self.pet.stage, "")
                    self.status_text = f"{self.pet.name} grew into a {stage_name}!"
                    self.status_timer = TARGET_FPS * 4
                    self.pet._prev_stage = self.pet.stage

                # State transition effects
                if new_state != prev_state:
                    sn = new_state.name
                    if sn == "HAPPY":
                        self.particles.emit_sparkles(WINDOW_SIZE // 2,
                                                     WINDOW_SIZE // 2 - 40)
                        self.sound.play("happy")
                    elif sn == "EATING":
                        self.particles.emit_hearts(WINDOW_SIZE // 2,
                                                   WINDOW_SIZE // 2)
                        self.sound.play("nom")
                    elif sn == "SLEEPING":
                        self.sound.play("yawn")
                    elif sn == "SAD":
                        self.sound.play("sad")
                    elif sn == "PLAYING":
                        self.sound.play("boing")
                    elif sn == "WALKING":
                        self.sound.play("step")

                # Check for story events
                ev = self.event_system.check_triggers(self.pet)
                if ev:
                    self.dialog.show(ev)

                # Blink logic
                now = time.time()
                if now - self.last_blink > self.next_blink:
                    self.slime.trigger_blink()
                    self.last_blink = now
                    self.next_blink = random.uniform(2.0, 6.0)

                # Update animation controller
                self.anim_ctrl.update(dt)

                # Copy animation values to slime for drawing
                self.slime.body_squash = self.anim_ctrl.body_squash
                self.slime.body_stretch = self.anim_ctrl.body_stretch
                self.slime.bounce = self.anim_ctrl.bounce
                self.slime.eye_scale = self.anim_ctrl.eye_scale
                self.slime.expression = self.anim_ctrl.expression
                self.slime.body_tint = self.anim_ctrl.body_tint
                self.slime.stage = self.pet.stage

                # Update blink state
                self.slime.update(dt)

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

    def _play_anim(self, name: str):
        clip = get_anim(name)
        self.anim_ctrl.play(clip)

    def _handle_action(self, action: str):
        if action == "quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        if action == "toggle_top":
            self.always_on_top = not getattr(self, 'always_on_top', False)
            self.wm.set_always_on_top(self.always_on_top)
            self.status_text = f"Always on top: {'ON' if self.always_on_top else 'OFF'}"
            self.status_timer = TARGET_FPS * 2
            self.config.set("always_on_top", self.always_on_top)
            self.config.save()
            return
        if action == "toggle_mute":
            muted = self.sound.toggle_mute()
            self.status_text = f"Sound: {'MUTED' if muted else 'ON'}"
            self.status_timer = TARGET_FPS * 2
            self.config.set("muted", muted)
            self.config.save()
            return
        response = self.pet.interact(action)
        if response:
            self.status_text = response
            self.status_timer = TARGET_FPS * 3
            # Play corresponding animation
            if action == "feed":
                self._play_anim("eat")
            elif action == "play":
                self._play_anim("play")
            elif action == "talk":
                self._play_anim("happy")
            elif action == "sleep":
                self._play_anim("sleep")
            elif action == "status":
                pass

    def _on_dialog_choice(self, outcome_id: str):
        """Handle a dialog choice being selected."""
        self.event_system.resolve_choice(outcome_id)
        self.dialog.dismiss()
        self.pet.state_machine._transition(PetState.IDLE)
        self._play_anim("idle")

    def _show_context_menu(self, pos):
        from context_menu import show_menu
        show_menu(pos, self._handle_action, self.screen)

    def _render(self):
        # Soft background
        self.screen.fill(P["bg"])

        # Draw the slime
        self.slime.draw(self.screen)

        # Draw crown for adult
        cy = int(WINDOW_SIZE // 2 + 15 + self.slime.bounce)
        stage_scale = STAGE_SCALES.get(self.pet.stage, 1.0)
        if self.pet.stage >= 3:
            self.slime.draw_crown(self.screen, WINDOW_SIZE // 2, cy, stage_scale)
        # Draw horns for teen+
        if self.pet.stage >= 2:
            self.slime.draw_horns(self.screen, WINDOW_SIZE // 2, cy, stage_scale)

        # Particles
        self.particles.draw(self.screen, (0, 0))

        # Dialog overlay
        if self.dialog.active:
            self.dialog.render(self.screen)

        # Status text
        if self.status_text and self.status_timer > 0:
            self._render_status_text()

        pygame.display.flip()

    def _render_status_text(self):
        font = pygame.font.Font(None, 16)
        lines = self.status_text.split('\n')
        y_offset = 8
        for line in lines:
            text_surf = font.render(line, True, (255, 255, 255))
            text_bg = pygame.Surface((text_surf.get_width() + 12,
                                      text_surf.get_height() + 6), pygame.SRCALPHA)
            text_bg.fill((0, 0, 0, 180))
            self.screen.blit(text_bg, (8, y_offset))
            self.screen.blit(text_surf, (14, y_offset + 3))
            y_offset += text_surf.get_height() + 4

    def _save(self):
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
