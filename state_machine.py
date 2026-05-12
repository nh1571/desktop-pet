"""Pet behavior state machine."""

import random
from enum import Enum, auto


class PetState(Enum):
    IDLE = auto()
    WALKING = auto()
    SLEEPING = auto()
    EATING = auto()
    PLAYING = auto()
    HAPPY = auto()
    SAD = auto()
    STORY = auto()
    CURIOUS = auto()
    DANCING = auto()
    CHASING_MOUSE = auto()

    def to_anim_name(self) -> str:
        mapping = {
            PetState.IDLE: "idle",
            PetState.WALKING: "walk",
            PetState.SLEEPING: "sleep",
            PetState.EATING: "eat",
            PetState.PLAYING: "play",
            PetState.HAPPY: "happy",
            PetState.SAD: "sad",
            PetState.STORY: "idle",
            PetState.CURIOUS: "curious",
            PetState.DANCING: "dance",
            PetState.CHASING_MOUSE: "walk",
        }
        return mapping.get(self, "idle")


class StateMachine:
    def __init__(self):
        self.state = PetState.IDLE
        self.state_timer = 0
        self.idle_timer = 0
        self.idle_duration = self._random_idle_duration()
        self.walk_target = (0, 0)
        self._interruptible = True

    def _random_idle_duration(self):
        return random.randint(60, 240)  # 5-20 seconds at 12 FPS

    @property
    def interruptible(self):
        return self._interruptible

    def update(self, pet):
        """Evaluate state transitions. Called every game tick."""
        self.state_timer += 1
        ns = pet.needs_system

        if self.state == PetState.IDLE:
            self._update_idle(pet, ns)
        elif self.state == PetState.WALKING:
            self._update_walking(pet)
        elif self.state == PetState.SLEEPING:
            self._update_sleeping(pet, ns)
        elif self.state in (PetState.EATING, PetState.PLAYING, PetState.HAPPY, PetState.SAD,
                            PetState.CURIOUS, PetState.DANCING):
            self._update_timed_state(pet)
        elif self.state == PetState.CHASING_MOUSE:
            self._update_chasing_mouse(pet)
        elif self.state == PetState.STORY:
            pass  # story state is managed externally

    def _update_idle(self, pet, ns):
        self.idle_timer += 1

        if ns.is_tired:
            self._transition(PetState.SLEEPING)
            return
        if ns.is_sad:
            self._transition(PetState.SAD)
            return

        if self.idle_timer >= self.idle_duration:
            self.idle_timer = 0
            self.idle_duration = self._random_idle_duration()
            # Pick a random autonomous behavior
            roll = random.random()
            if roll < 0.35:
                self._transition(PetState.WALKING)
            elif roll < 0.55:
                self._transition(PetState.DANCING)
            elif roll < 0.65:
                self._transition(PetState.CURIOUS)
            elif roll < 0.72 and ns.needs.happiness > 40:
                self._transition(PetState.HAPPY)
            else:
                self._transition(PetState.WALKING)

    def _update_walking(self, pet):
        wm = getattr(pet, 'wm', None)
        if wm is None:
            if self.state_timer > 40:
                self._transition(PetState.IDLE)
            return

        # Set walk target on first tick
        if self.state_timer == 1:
            wx, wy = wm.get_position()
            bounds = pet.screen_size
            # Pick random nearby position within screen
            dx = random.randint(-60, 60)
            dy = random.randint(-40, 40)
            tx = max(0, min(bounds[0] - 160, wx + dx))
            ty = max(0, min(bounds[1] - 160, wy + dy))
            self.walk_target = (tx, ty)

        # Lerp toward target
        if self.walk_target != (0, 0):
            wx, wy = wm.get_position()
            tx, ty = self.walk_target
            # Smooth step: move ~20% of remaining distance per tick
            new_x = int(wx + (tx - wx) * 0.2)
            new_y = int(wy + (ty - wy) * 0.2)
            wm.set_position(new_x, new_y)
            # Snap if close enough
            if abs(tx - new_x) < 3 and abs(ty - new_y) < 3:
                wm.set_position(tx, ty)

        if self.state_timer > 40:  # ~3 seconds
            self.walk_target = (0, 0)
            self._transition(PetState.IDLE)

    def _update_sleeping(self, pet, ns):
        # Restore energy while sleeping
        pet.needs_system.modify(energy=0.15)
        if ns.needs.energy > 70 or self.state_timer > 600:  # ~50 sec max
            self._transition(PetState.IDLE)

    def _update_timed_state(self, pet):
        durations = {
            PetState.EATING: 30, PetState.PLAYING: 40,
            PetState.HAPPY: 25, PetState.SAD: 25,
            PetState.CURIOUS: 35, PetState.DANCING: 45,
        }
        max_t = durations.get(self.state, 30)
        if self.state_timer > max_t:
            self._transition(PetState.IDLE)

    def _update_chasing_mouse(self, pet):
        """Chase the mouse cursor position."""
        import pygame
        wm = getattr(pet, 'wm', None)
        if wm is None or self.state_timer > 50:
            self._transition(PetState.IDLE)
            return
        mx, my = pygame.mouse.get_pos()
        wx, wy = wm.get_position()
        tx = max(0, min(pet.screen_size[0] - 160, mx - 60))
        ty = max(0, min(pet.screen_size[1] - 160, my - 60))
        new_x = int(wx + (tx - wx) * 0.1)
        new_y = int(wy + (ty - wy) * 0.1)
        wm.set_position(new_x, new_y)

    def _transition(self, new_state: PetState):
        self.state = new_state
        self.state_timer = 0
        self._interruptible = new_state not in (PetState.EATING, PetState.PLAYING)

    def _transition(self, new_state: PetState):
        self.state = new_state
        self.state_timer = 0
        self._interruptible = new_state not in (PetState.EATING, PetState.PLAYING)

    def request(self, new_state: PetState) -> bool:
        """External request to change state. Returns True if accepted."""
        if not self._interruptible:
            return False
        self._transition(new_state)
        return True

    def wake_up(self):
        if self.state == PetState.SLEEPING:
            self._transition(PetState.IDLE)
