"""Story event definitions and trigger system."""

import random
from dataclasses import dataclass, field

from config import STAGE_BABY, STAGE_CHILD, STAGE_TEEN, STAGE_ADULT


@dataclass
class StoryEvent:
    event_id: str
    title: str
    text: str
    trigger_stage: int = STAGE_BABY
    trigger_playtime_min: float = 0.0
    trigger_needs: dict = field(default_factory=dict)
    trigger_random: float = 0.01
    one_shot: bool = True
    prereq_events: list = field(default_factory=list)
    choices: list = field(default_factory=list)  # [(label, outcome_id), ...]


EVENTS: list[StoryEvent] = [
    # ═══════════════════════════════════════════
    # BABY STAGE
    # ═══════════════════════════════════════════
    StoryEvent(
        event_id="first_hunger",
        title="So Hungry...",
        text=(
            "Your slime wobbles sadly.\n"
            "It's never felt this before.\n"
            "A strange emptiness inside...\n"
            "Maybe try feeding it?"
        ),
        trigger_stage=STAGE_BABY,
        trigger_playtime_min=3.0,
        trigger_needs={"hunger": (0, 50)},
        trigger_random=0.08,
    ),
    StoryEvent(
        event_id="first_play",
        title="Let's Play!",
        text=(
            "Your slime bounces excitedly!\n"
            "It wants to play with you.\n"
            "Right-click and choose Play!"
        ),
        trigger_stage=STAGE_BABY,
        trigger_playtime_min=5.0,
        trigger_needs={"happiness": (0, 50)},
        trigger_random=0.06,
    ),
    StoryEvent(
        event_id="baby_discovery",
        title="What's This?",
        text=(
            "The slime stares at the screen.\n"
            "So many colors... so many words...\n"
            "It tilts its head, confused.\n"
            "'Bloop?'"
        ),
        trigger_stage=STAGE_BABY,
        trigger_playtime_min=10.0,
        trigger_random=0.02,
    ),
    StoryEvent(
        event_id="baby_tired",
        title="Sleepy Slime",
        text=(
            "The baby slime's eyes droop.\n"
            "It yawns — a tiny bubble pops.\n"
            "Maybe it's time for a nap."
        ),
        trigger_stage=STAGE_BABY,
        trigger_needs={"energy": (0, 25)},
        trigger_random=0.06,
    ),

    # ═══════════════════════════════════════════
    # CHILD STAGE
    # ═══════════════════════════════════════════
    StoryEvent(
        event_id="growing_pains",
        title="Growing Pains",
        text=(
            "Something feels different today.\n"
            "Your slime is... bigger?\n"
            "And those bumps on its head —\n"
            "are those horns?!"
        ),
        trigger_stage=STAGE_CHILD,
        trigger_playtime_min=120.0,
        trigger_random=0.04,
        one_shot=True,
        prereq_events=["first_hunger"],
    ),
    StoryEvent(
        event_id="best_friend",
        title="Best Friend",
        text=(
            "Your slime looks up at you.\n"
            "'You know... you're my best friend.'\n"
            "It blushes green.\n"
            "You are its whole world."
        ),
        trigger_stage=STAGE_CHILD,
        trigger_playtime_min=180.0,
        trigger_random=0.02,
        one_shot=True,
    ),
    StoryEvent(
        event_id="curious_slime",
        title="Whatcha Doin?",
        text=(
            "The slime peers at your keyboard.\n"
            "'What are all those buttons for?'\n"
            "'Can I push one?'\n"
            "It reaches out a tiny pseudopod..."
        ),
        trigger_stage=STAGE_CHILD,
        trigger_playtime_min=200.0,
        trigger_random=0.03,
    ),
    StoryEvent(
        event_id="snack_time",
        title="Snack Time!",
        text=(
            "Your slime found a cookie crumb\n"
            "on the desktop!\n"
            "...it's not a real cookie.\n"
            "But the slime doesn't know that. :)"
        ),
        trigger_stage=STAGE_CHILD,
        trigger_playtime_min=150.0,
        trigger_random=0.03,
    ),

    # ═══════════════════════════════════════════
    # TEEN STAGE
    # ═══════════════════════════════════════════
    StoryEvent(
        event_id="identity_crisis",
        title="Who Am I?",
        text=(
            "The teen slime stares at its reflection.\n"
            "'What AM I, really?'\n"
            "'Just a blob on a screen?'\n"
            "'Or something... more?'"
        ),
        trigger_stage=STAGE_TEEN,
        trigger_playtime_min=500.0,
        trigger_random=0.03,
        one_shot=True,
        choices=[("You're my friend!", "friend"), ("You're a slime, dude.", "slime")],
    ),
    StoryEvent(
        event_id="rebel_phase",
        title="You Don't Own Me!",
        text=(
            "The slime crosses its... arms?\n"
            "'I don't HAVE to be cute!' it pouts.\n"
            "(But it is still very cute.)"
        ),
        trigger_stage=STAGE_TEEN,
        trigger_playtime_min=550.0,
        trigger_random=0.03,
        prereq_events=["identity_crisis"],
    ),
    StoryEvent(
        event_id="slime_philosophy",
        title="Deep Thoughts",
        text=(
            "The slime gazes into the distance.\n"
            "'If a slime bounces in a forest\n"
            "and no one is around to see it...'\n"
            "'does it still go bloop?'"
        ),
        trigger_stage=STAGE_TEEN,
        trigger_playtime_min=600.0,
        trigger_random=0.03,
    ),
    StoryEvent(
        event_id="ambition",
        title="Big Dreams",
        text=(
            "The slime has made a decision.\n"
            "'I'm going to be the BEST\n"
            "desktop pet there ever was!'\n"
            "It strikes a determined pose."
        ),
        trigger_stage=STAGE_TEEN,
        trigger_playtime_min=650.0,
        trigger_random=0.02,
        one_shot=True,
        choices=[("I believe in you!", "cheer"), ("Sure you will...", "doubt")],
    ),

    # ═══════════════════════════════════════════
    # ADULT STAGE
    # ═══════════════════════════════════════════
    StoryEvent(
        event_id="wisdom",
        title="Slime Wisdom",
        text=(
            "The adult slime smiles knowingly.\n"
            "'You know, happiness is like\n"
            "a bouncy blob — the harder you\n"
            "squeeze, the less you feel it.'"
        ),
        trigger_stage=STAGE_ADULT,
        trigger_playtime_min=1500.0,
        trigger_random=0.02,
    ),
    StoryEvent(
        event_id="gratitude",
        title="Thank You",
        text=(
            "The slime looks at you warmly.\n"
            "'Thank you for taking care of me\n"
            "all this time.'\n"
            "'I couldn't ask for a better human.'"
        ),
        trigger_stage=STAGE_ADULT,
        trigger_playtime_min=1600.0,
        trigger_random=0.02,
        one_shot=True,
        choices=[("You're welcome! <3", "warm"), ("No problem, blob.", "cool")],
    ),
    StoryEvent(
        event_id="legacy",
        title="A Slime's Legacy",
        text=(
            "The slime reflects on its journey.\n"
            "From a tiny blob to who it is today.\n"
            "'You know... life is pretty good\n"
            "on this desktop.'"
        ),
        trigger_stage=STAGE_ADULT,
        trigger_playtime_min=1800.0,
        trigger_random=0.02,
        one_shot=True,
    ),
]


class EventSystem:
    def __init__(self):
        self.events = EVENTS
        self.check_timer = 0
        self.check_interval = 60  # ticks between checks (~5s at 12 FPS)
        self.current_event: StoryEvent | None = None

    def check_triggers(self, pet) -> StoryEvent | None:
        """Check if any event should trigger. Returns event or None."""
        self.check_timer += 1
        if self.check_timer < self.check_interval:
            return None
        self.check_timer = 0

        for event in self.events:
            if event.one_shot and event.event_id in pet.event_flags:
                continue
            if pet.stage < event.trigger_stage:
                continue
            if pet.playtime < event.trigger_playtime_min:
                continue
            if event.prereq_events:
                if not all(eid in pet.event_flags for eid in event.prereq_events):
                    continue
            if event.trigger_needs:
                match = True
                ns = pet.needs_system
                for need, (lo, hi) in event.trigger_needs.items():
                    val = getattr(ns.needs, need)
                    if not (lo <= val <= hi):
                        match = False
                        break
                if not match:
                    continue
            if random.random() < event.trigger_random:
                pet.event_flags.add(event.event_id)
                self.current_event = event
                return event
        return None

    def resolve_choice(self, outcome_id: str):
        """Handle a choice outcome. Modify pet state based on the outcome."""
        self.current_event = None

    def dismiss_current(self):
        self.current_event = None
