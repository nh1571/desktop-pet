"""SDL2 window control: always-on-top, opacity, borderless, positioning."""

import ctypes
import os
import pygame


class WindowManager:
    def __init__(self):
        self._sdl = None
        self._win = None

    def init(self):
        sdl_path = os.path.join(
            os.path.dirname(pygame.__file__),
            '.dylibs', 'libSDL2-2.0.0.dylib'
        )
        if not os.path.exists(sdl_path):
            raise RuntimeError(f"SDL2 dylib not found at {sdl_path}")

        self._sdl = ctypes.CDLL(sdl_path)
        self._sdl.SDL_GetWindowFromID.argtypes = [ctypes.c_uint32]
        self._sdl.SDL_GetWindowFromID.restype = ctypes.c_void_p
        self._sdl.SDL_SetWindowAlwaysOnTop.argtypes = [
            ctypes.c_void_p, ctypes.c_int
        ]
        self._sdl.SDL_SetWindowAlwaysOnTop.restype = None

    def bind(self, window):
        """Bind to a pygame._sdl2.Window after display is created."""
        self._win = window
        self._win.borderless = True

    def set_always_on_top(self, enable: bool):
        if not self._sdl or not self._win:
            return
        sdl_win = self._sdl.SDL_GetWindowFromID(self._win.id)
        self._sdl.SDL_SetWindowAlwaysOnTop(sdl_win, 1 if enable else 0)

    def set_opacity(self, value: float):
        if self._win:
            self._win.opacity = max(0.1, min(1.0, value))

    def set_position(self, x: int, y: int):
        if self._win:
            self._win.position = (x, y)

    def get_position(self):
        if self._win:
            return self._win.position
        return (100, 100)

    def focus(self):
        if self._win:
            self._win.focus()
