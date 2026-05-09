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

    def to_anim_name(self) -> str:
        mapping = {
            PetState.IDLE: "idle",
            PetState.WALKING: "walk",
            PetState.SLEEPING: "sleep",
            PetState.EATING: "eat",
            PetState.PLAYING: "play",
            PetState.HAPPY: "happy",
            PetState.SAD: "sad",
            PetState.STORY: "idle",  # story uses dialog overlay
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
        elif self.state in (PetState.EATING, PetState.PLAYING, PetState.HAPPY, PetState.SAD):
            self._update_timed_state(pet)
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
            self._transition(PetState.WALKING)

    def _update_walking(self, pet):
        if self.state_timer > 40:  # ~3 seconds
            self._transition(PetState.IDLE)

    def _update_sleeping(self, pet, ns):
        # Wake up when energy is restored
        if ns.needs.energy > 70 or self.state_timer > 600:  # ~50 sec max
            self._transition(PetState.IDLE)

    def _update_timed_state(self, pet):
        if self.state_timer > 30:  # ~2.5 sec for eat/play/happy/sad
            self._transition(PetState.IDLE)

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
