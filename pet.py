"""Core Pet class — orchestrates needs, state machine, animation, and growth."""

import time

from config import (
    STAGE_BABY, STAGE_CHILD, STAGE_TEEN, STAGE_ADULT,
    STAGE_NAMES, TARGET_FPS, MAX_NEED,
)
from needs import NeedsSystem, Needs
from state_machine import StateMachine, PetState
from sprites import STAGE_SPRITES
from animation import Anim, AnimPlayer
from sprite_renderer import SpriteRenderer


class Pet:
    def __init__(self, renderer: SpriteRenderer, anim_player: AnimPlayer):
        self.renderer = renderer
        self.anim_player = anim_player
        self.name = "Slimy"
        self.stage = STAGE_BABY
        self.playtime = 0.0  # total playtime in minutes
        self.needs_system = NeedsSystem()
        self.state_machine = StateMachine()
        self.event_flags: set[str] = set()
        self.facing_right = True

        # Track previous state to detect transitions
        self._prev_state = None

    @property
    def needs(self):
        return self.needs_system.needs

    def update(self, speed: float = 1.0):
        """Main update tick — called every frame."""
        self.needs_system.update(speed)
        self.playtime += (1.0 / TARGET_FPS / 60.0) * speed
        self._check_growth()

        prev_state = self.state_machine.state
        self.state_machine.update(self)

        # If state changed, play new animation
        if self.state_machine.state != prev_state:
            anim_name = self.state_machine.state.to_anim_name()
            # Don't interrupt story state
            if self.state_machine.state != PetState.STORY:
                self._play_anim(anim_name)

        self.anim_player.update()

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
            self.stage = new_stage
            # Refresh animation with new stage sprites
            anim_name = self.state_machine.state.to_anim_name()
            self._play_anim(anim_name)

    def _play_anim(self, name: str):
        sprites = STAGE_SPRITES[self.stage]
        frames = sprites.get(name, sprites.get("idle"))
        if frames:
            self.anim_player.play(name, Anim(name=name, frames=frames))

    def interact(self, action: str) -> str | None:
        """Handle user interaction. Returns optional response text."""
        sm = self.state_machine

        if action == "feed":
            if not sm.request(PetState.EATING):
                return "I'm busy right now!"
            self.needs_system.modify(hunger=30, energy=5)
            self._play_anim("eat")
            return "*nom nom nom*"

        elif action == "play":
            if not sm.request(PetState.PLAYING):
                return "I'm busy right now!"
            self.needs_system.modify(happiness=30, energy=-15)
            self._play_anim("play")
            return "*bounce bounce*"

        elif action == "talk":
            sm.request(PetState.HAPPY)
            self.needs_system.modify(happiness=5)
            self._play_anim("happy")
            return self._random_greeting()

        elif action == "sleep":
            sm.request(PetState.SLEEPING)
            self._play_anim("sleep")
            return "zzz..."

        elif action == "status":
            return self.get_status_text()

        return None

    def _random_greeting(self) -> str:
        import random
        greetings = {
            STAGE_BABY: [
                "Goo goo!",
                "*wobble*",
                "Bloop!",
                "*squeak*",
            ],
            STAGE_CHILD: [
                "Hi friend!",
                "Play with me?",
                "I found a bug today!",
                "Bouncy bouncy!",
            ],
            STAGE_TEEN: [
                "Whatcha doin?",
                "I've been thinking...",
                "Nice day, huh?",
                "You're my favorite human.",
            ],
            STAGE_ADULT: [
                "Back so soon?",
                "I was meditating.",
                "The desktop is peaceful today.",
                "You look productive!",
            ],
        }
        g = greetings.get(self.stage, greetings[STAGE_BABY])
        return random.choice(g)

    def get_status_text(self) -> str:
        return (
            f"  {self.name} | {STAGE_NAMES[self.stage]}\n"
            f"  {'=' * 20}\n"
            f"  Hunger:    {'#' * int(self.needs.hunger / 10)}{'.' * int(10 - self.needs.hunger / 10)}\n"
            f"  Happiness: {'#' * int(self.needs.happiness / 10)}{'.' * int(10 - self.needs.happiness / 10)}\n"
            f"  Energy:    {'#' * int(self.needs.energy / 10)}{'.' * int(10 - self.needs.energy / 10)}\n"
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
