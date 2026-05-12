"""Core Pet class — orchestrates needs, state machine, and growth."""

from config import (
    STAGE_BABY, STAGE_CHILD, STAGE_TEEN, STAGE_ADULT,
    STAGE_NAMES, TARGET_FPS, MAX_NEED,
)
from needs import NeedsSystem, Needs
from state_machine import StateMachine, PetState


class Pet:
    def __init__(self, window_manager=None, screen_size=(1920, 1080)):
        self.wm = window_manager
        self.screen_size = screen_size
        self.name = "Slimy"
        self.stage = STAGE_BABY
        self.playtime = 0.0  # total playtime in minutes
        self.needs_system = NeedsSystem()
        self.state_machine = StateMachine()
        self.event_flags: set[str] = set()
        self.facing_right = True
        self._prev_stage = self.stage

    @property
    def needs(self):
        return self.needs_system.needs

    @property
    def just_grew_up(self) -> bool:
        return self._prev_stage != self.stage

    def update(self, speed: float = 1.0):
        """Main update tick — called every frame."""
        self.needs_system.update(speed)
        self.playtime += (1.0 / TARGET_FPS / 60.0) * speed
        self._check_growth()

        prev_state = self.state_machine.state
        self.state_machine.update(self)

    def _check_growth(self):
        if self.playtime >= STAGE_ADULT:
            new_stage = STAGE_ADULT
        elif self.playtime >= STAGE_TEEN:
            new_stage = STAGE_TEEN
        elif self.playtime >= STAGE_CHILD:
            new_stage = STAGE_CHILD
        else:
            new_stage = STAGE_BABY

        if new_stage != self.stage:
            self._prev_stage = self.stage
            self.stage = new_stage

    def interact(self, action: str) -> str | None:
        """Handle user interaction. Returns optional response text."""
        sm = self.state_machine

        if action == "feed":
            if not sm.request(PetState.EATING):
                return "I'm busy right now!"
            self.needs_system.modify(hunger=30, energy=5)
            return "*nom nom nom*"

        elif action == "play":
            if not sm.request(PetState.PLAYING):
                return "I'm busy right now!"
            self.needs_system.modify(happiness=30, energy=-15)
            return "*bounce bounce*"

        elif action == "talk":
            sm.request(PetState.HAPPY)
            self.needs_system.modify(happiness=5)
            return self._random_greeting()

        elif action == "sleep":
            sm.request(PetState.SLEEPING)
            return "zzz..."

        elif action == "status":
            return self.get_status_text()

        return None

    def _random_greeting(self) -> str:
        import random
        greetings = {
            STAGE_BABY: ["Goo goo!", "*wobble*", "Bloop!", "*squeak*"],
            STAGE_CHILD: ["Hi friend!", "Play with me?", "I found a bug today!",
                          "Bouncy bouncy!"],
            STAGE_TEEN: ["Whatcha doin?", "I've been thinking...",
                         "Nice day, huh?", "You're my favorite human."],
            STAGE_ADULT: ["Back so soon?", "I was meditating.",
                          "The desktop is peaceful today.", "You look productive!"],
        }
        g = greetings.get(self.stage, greetings[STAGE_BABY])
        return random.choice(g)

    def get_status_text(self) -> str:
        return (
            f"  {self.name} | {STAGE_NAMES[self.stage]}\n"
            f"  {'=' * 20}\n"
            f"  Hunger:    {'#' * int(self.needs.hunger / 10)}"
            f"{'.' * int(10 - self.needs.hunger / 10)}\n"
            f"  Happiness: {'#' * int(self.needs.happiness / 10)}"
            f"{'.' * int(10 - self.needs.happiness / 10)}\n"
            f"  Energy:    {'#' * int(self.needs.energy / 10)}"
            f"{'.' * int(10 - self.needs.energy / 10)}\n"
            f"  Playtime:  {self.playtime:.0f} min"
        )

    def to_dict(self):
        return {
            "name": self.name,
            "stage": self.stage,
            "playtime": self.playtime,
            "needs": self.needs_system.to_dict(),
            "event_flags": list(self.event_flags),
        }

    def restore_from_dict(self, d: dict):
        self.name = d.get("name", "Slimy")
        self.stage = d["stage"]
        self.playtime = d["playtime"]
        self.needs_system = NeedsSystem(Needs(**d["needs"]))
        self.event_flags = set(d.get("event_flags", []))
