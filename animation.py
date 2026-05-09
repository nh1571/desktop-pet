"""Animation player: frame timing, looping, and transitions."""

from dataclasses import dataclass, field

import pygame

from sprite_renderer import SpriteRenderer


@dataclass
class Anim:
    name: str
    frames: list  # [(pixel_grid, duration_ticks), ...]
    loop: bool = True

    def __post_init__(self):
        self.frame_count = len(self.frames)

    @property
    def total_ticks(self):
        return sum(d for _, d in self.frames)


@dataclass
class AnimState:
    anim: Anim | None = None
    frame_index: int = 0
    tick_counter: int = 0
    finished: bool = False
    _anim_name: str = ""


class AnimPlayer:
    def __init__(self, renderer: SpriteRenderer):
        self.renderer = renderer
        self.state = AnimState()

    def play(self, name: str, anim: Anim | None):
        if anim is None:
            return
        if self.state._anim_name == name and not self.state.finished:
            return  # don't restart same running anim
        self.state.anim = anim
        self.state._anim_name = name
        self.state.frame_index = 0
        self.state.tick_counter = 0
        self.state.finished = False

    def update(self):
        if self.state.anim is None or self.state.finished:
            return
        self.state.tick_counter += 1
        _, duration = self.state.anim.frames[self.state.frame_index]
        if self.state.tick_counter >= duration:
            self.state.tick_counter = 0
            if self.state.frame_index < self.state.anim.frame_count - 1:
                self.state.frame_index += 1
            elif self.state.anim.loop:
                self.state.frame_index = 0
            else:
                self.state.finished = True

    def get_surface(self) -> pygame.Surface | None:
        if self.state.anim is None:
            return None
        grid, _ = self.state.anim.frames[self.state.frame_index]
        return self.renderer.render(grid)

    @property
    def current_anim(self) -> str:
        return self.state._anim_name

    @property
    def is_finished(self) -> bool:
        return self.state.finished
