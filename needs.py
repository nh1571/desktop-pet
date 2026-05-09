"""Needs system: hunger, happiness, energy with real-time decay."""

import time
from dataclasses import dataclass

from config import (
    HUNGER_DECAY_PER_HOUR,
    HAPPINESS_DECAY_PER_HOUR,
    ENERGY_DECAY_PER_HOUR,
    MAX_NEED,
    HUNGRY_THRESHOLD,
    STARVING_THRESHOLD,
    TIRED_THRESHOLD,
    SAD_THRESHOLD,
)


@dataclass
class Needs:
    hunger: float = 80.0
    happiness: float = 70.0
    energy: float = 90.0


class NeedsSystem:
    def __init__(self, needs: Needs | None = None):
        self.needs = needs or Needs()
        self.last_update = time.time()

    def update(self, speed: float = 1.0):
        """Decay needs based on elapsed real time. speed > 1 for fast mode."""
        now = time.time()
        elapsed_hours = (now - self.last_update) / 3600.0
        self.last_update = now

        self.needs.hunger = max(
            0, self.needs.hunger - HUNGER_DECAY_PER_HOUR * elapsed_hours * speed
        )
        self.needs.happiness = max(
            0, self.needs.happiness - HAPPINESS_DECAY_PER_HOUR * elapsed_hours * speed
        )
        self.needs.energy = max(
            0, self.needs.energy - ENERGY_DECAY_PER_HOUR * elapsed_hours * speed
        )

    def modify(self, hunger: float = 0, happiness: float = 0, energy: float = 0):
        self.needs.hunger = min(MAX_NEED, max(0, self.needs.hunger + hunger))
        self.needs.happiness = min(MAX_NEED, max(0, self.needs.happiness + happiness))
        self.needs.energy = min(MAX_NEED, max(0, self.needs.energy + energy))

    @property
    def is_hungry(self):
        return self.needs.hunger < HUNGRY_THRESHOLD

    @property
    def is_starving(self):
        return self.needs.hunger < STARVING_THRESHOLD

    @property
    def is_tired(self):
        return self.needs.energy < TIRED_THRESHOLD

    @property
    def is_sad(self):
        return self.needs.happiness < SAD_THRESHOLD

    @property
    def worst_need(self) -> str:
        """Return the name of the lowest need as a percentage."""
        h = self.needs.hunger / MAX_NEED
        p = self.needs.happiness / MAX_NEED
        e = self.needs.energy / MAX_NEED
        worst = min(h, p, e)
        if worst == h:
            return "hunger"
        elif worst == p:
            return "happiness"
        return "energy"

    def to_dict(self):
        return {
            "hunger": self.needs.hunger,
            "happiness": self.needs.happiness,
            "energy": self.needs.energy,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(Needs(**d))
