"""Vector animation: keyframe interpolation with easing for the slime."""

from dataclasses import dataclass, field
import random


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_quad(t: float) -> float:
    return 1 - (1 - t) ** 2


def ease_in_out_quad(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2


def ease_out_elastic(t: float) -> float:
    if t == 0 or t == 1:
        return t
    import math
    return math.pow(2, -10 * t) * math.sin((t - 0.075) * 2 * math.pi / 0.3) + 1


@dataclass
class AnimKeyframe:
    """A single keyframe with target values and duration."""
    body_squash: float = 1.0
    body_stretch: float = 1.0
    bounce: float = 0.0
    eye_scale: float = 1.0
    expression: str = "neutral"
    body_tint: tuple | None = None
    duration: float = 0.5  # seconds


@dataclass
class AnimClip:
    """An animation clip made of keyframes."""
    name: str
    keyframes: list[AnimKeyframe]
    loop: bool = True

    @property
    def total_duration(self) -> float:
        return sum(kf.duration for kf in self.keyframes)


class AnimController:
    """Controls animation state: which clip is playing, interpolation between keyframes."""

    def __init__(self):
        self.current: AnimClip | None = None
        self._clip_time: float = 0.0
        self._kf_index: int = 0
        self._kf_time: float = 0.0
        self._prev_kf: AnimKeyframe | None = None
        self._finished: bool = False

        # Output values (read by VectorSlime each frame)
        self.body_squash: float = 1.0
        self.body_stretch: float = 1.0
        self.bounce: float = 0.0
        self.eye_scale: float = 1.0
        self.expression: str = "neutral"
        self.body_tint: tuple | None = None

    def play(self, clip: AnimClip):
        if self.current and self.current.name == clip.name:
            return  # already playing
        self.current = clip
        self._clip_time = 0.0
        self._kf_index = 0
        self._kf_time = 0.0
        self._prev_kf = None
        self._finished = False
        # Snap to first keyframe
        if clip.keyframes:
            kf = clip.keyframes[0]
            self._apply(kf)

    def update(self, dt: float):
        if not self.current or not self.current.keyframes:
            return
        if self._finished:
            return

        clip = self.current
        self._clip_time += dt
        self._kf_time += dt

        kf = clip.keyframes[self._kf_index]

        if self._kf_time >= kf.duration:
            # Advance to next keyframe
            self._prev_kf = kf
            self._kf_index += 1
            self._kf_time -= kf.duration

            if self._kf_index >= len(clip.keyframes):
                if clip.loop:
                    self._kf_index = 0
                    self._kf_time = 0.0
                    self._prev_kf = clip.keyframes[-1]
                else:
                    self._finished = True
                    # Snap to last keyframe
                    self._apply(clip.keyframes[-1])
                    return

            kf = clip.keyframes[self._kf_index]

        # Determine start keyframe for interpolation
        start = self._prev_kf if self._prev_kf is not None else kf
        if self._prev_kf is None:
            t = 0.0
        else:
            dur = kf.duration
            if dur > 0:
                t_raw = self._kf_time / dur
            else:
                t_raw = 1.0
            t = ease_in_out_quad(min(1.0, max(0.0, t_raw)))

        # Interpolate
        self.body_squash = lerp(start.body_squash, kf.body_squash, t)
        self.body_stretch = lerp(start.body_stretch, kf.body_stretch, t)
        self.bounce = lerp(start.bounce, kf.bounce, t)
        self.eye_scale = lerp(start.eye_scale, kf.eye_scale, t)
        self.expression = kf.expression if t > 0.5 else start.expression
        self.body_tint = kf.body_tint if t > 0.5 else start.body_tint

    def _apply(self, kf: AnimKeyframe):
        self.body_squash = kf.body_squash
        self.body_stretch = kf.body_stretch
        self.bounce = kf.bounce
        self.eye_scale = kf.eye_scale
        self.expression = kf.expression
        self.body_tint = kf.body_tint

    @property
    def finished(self) -> bool:
        return self._finished


# ═══════════════════════════════════════════
# Pre-defined Animation Clips
# ═══════════════════════════════════════════

ANIM_IDLE = AnimClip("idle", [
    AnimKeyframe(body_squash=1.0, body_stretch=1.0, eye_scale=1.0,
                 expression="neutral", duration=1.2),
    AnimKeyframe(body_squash=1.03, body_stretch=0.97, eye_scale=1.0,
                 expression="neutral", duration=1.2),
], loop=True)

ANIM_HAPPY = AnimClip("happy", [
    AnimKeyframe(body_squash=1.05, body_stretch=0.95, bounce=-4, eye_scale=1.1,
                 expression="very_happy", duration=0.3),
    AnimKeyframe(body_squash=0.97, body_stretch=1.03, bounce=-8, eye_scale=1.1,
                 expression="very_happy", duration=0.3),
], loop=True)

ANIM_SAD = AnimClip("sad", [
    AnimKeyframe(body_squash=0.98, body_stretch=0.95, bounce=0, eye_scale=0.85,
                 expression="sad", body_tint=(110, 195, 110), duration=1.0),
    AnimKeyframe(body_squash=1.0, body_stretch=0.93, bounce=0, eye_scale=0.85,
                 expression="sad", body_tint=(105, 190, 105), duration=1.0),
], loop=True)

ANIM_EAT = AnimClip("eat", [
    AnimKeyframe(body_squash=1.0, body_stretch=1.0, bounce=0, eye_scale=1.0,
                 expression="neutral", duration=0.4),
    AnimKeyframe(body_squash=1.08, body_stretch=0.9, bounce=0, eye_scale=0.9,
                 expression="eating", duration=0.4),
    AnimKeyframe(body_squash=1.02, body_stretch=0.98, bounce=0, eye_scale=1.0,
                 expression="happy", duration=0.3),
], loop=True)

ANIM_PLAY = AnimClip("play", [
    AnimKeyframe(body_squash=1.15, body_stretch=0.7, bounce=5, eye_scale=1.0,
                 expression="happy", duration=0.25),  # squash down
    AnimKeyframe(body_squash=0.85, body_stretch=1.25, bounce=-25, eye_scale=1.15,
                 expression="very_happy", duration=0.3),  # launch up
    AnimKeyframe(body_squash=1.1, body_stretch=0.85, bounce=-5, eye_scale=1.05,
                 expression="happy", duration=0.25),  # land
], loop=True)

ANIM_SLEEP = AnimClip("sleep", [
    AnimKeyframe(body_squash=0.98, body_stretch=0.9, bounce=0, eye_scale=0.05,
                 expression="sleeping", duration=2.0),
    AnimKeyframe(body_squash=1.0, body_stretch=0.88, bounce=0, eye_scale=0.05,
                 expression="sleeping", duration=2.0),
], loop=True)

ANIM_WALK = AnimClip("walk", [
    AnimKeyframe(body_squash=1.05, body_stretch=0.95, bounce=2, eye_scale=1.0,
                 expression="neutral", duration=0.2),
    AnimKeyframe(body_squash=0.97, body_stretch=1.05, bounce=-6, eye_scale=1.0,
                 expression="neutral", duration=0.2),
    AnimKeyframe(body_squash=1.06, body_stretch=0.93, bounce=2, eye_scale=1.0,
                 expression="neutral", duration=0.2),
    AnimKeyframe(body_squash=0.96, body_stretch=1.06, bounce=-6, eye_scale=1.0,
                 expression="neutral", duration=0.2),
], loop=True)

# ── New expression clips ──

ANIM_CURIOUS = AnimClip("curious", [
    AnimKeyframe(body_squash=1.02, body_stretch=0.98, bounce=0, eye_scale=1.05,
                 expression="curious", duration=0.6),
    AnimKeyframe(body_squash=1.05, body_stretch=0.95, bounce=-3, eye_scale=1.1,
                 expression="curious", duration=0.6),
], loop=True)

ANIM_SURPRISED = AnimClip("surprised", [
    AnimKeyframe(body_squash=0.95, body_stretch=1.08, bounce=-8, eye_scale=1.25,
                 expression="surprised", duration=0.3),
    AnimKeyframe(body_squash=1.0, body_stretch=1.0, bounce=-3, eye_scale=1.25,
                 expression="surprised", duration=0.3),
], loop=False)

ANIM_EXCITED = AnimClip("excited", [
    AnimKeyframe(body_squash=1.1, body_stretch=0.8, bounce=8, eye_scale=1.2,
                 expression="excited", duration=0.2),
    AnimKeyframe(body_squash=0.88, body_stretch=1.18, bounce=-18, eye_scale=1.3,
                 expression="excited", duration=0.25),
    AnimKeyframe(body_squash=1.08, body_stretch=0.85, bounce=4, eye_scale=1.2,
                 expression="excited", duration=0.2),
], loop=True)

ANIM_MISCHIEVOUS = AnimClip("mischievous", [
    AnimKeyframe(body_squash=1.03, body_stretch=0.97, bounce=0, eye_scale=0.9,
                 expression="mischievous", duration=0.5),
    AnimKeyframe(body_squash=1.06, body_stretch=0.94, bounce=-2, eye_scale=0.85,
                 expression="mischievous", duration=0.5),
], loop=True)

ANIM_DIZZY = AnimClip("dizzy", [
    AnimKeyframe(body_squash=1.0, body_stretch=0.95, bounce=0, eye_scale=0.9,
                 expression="dizzy", body_tint=(130, 210, 130), duration=0.4),
    AnimKeyframe(body_squash=1.04, body_stretch=0.92, bounce=0, eye_scale=0.9,
                 expression="dizzy", body_tint=(125, 205, 125), duration=0.4),
], loop=True)

ANIM_LOVING = AnimClip("loving", [
    AnimKeyframe(body_squash=1.02, body_stretch=0.98, bounce=-3, eye_scale=0.95,
                 expression="loving", body_tint=(255, 180, 180), duration=0.6),
    AnimKeyframe(body_squash=1.04, body_stretch=0.96, bounce=-5, eye_scale=0.95,
                 expression="loving", body_tint=(255, 175, 175), duration=0.6),
], loop=True)

ANIM_DANCE = AnimClip("dance", [
    AnimKeyframe(body_squash=1.1, body_stretch=0.85, bounce=6, eye_scale=1.1,
                 expression="very_happy", duration=0.3),
    AnimKeyframe(body_squash=0.9, body_stretch=1.15, bounce=-12, eye_scale=1.1,
                 expression="very_happy", duration=0.3),
    AnimKeyframe(body_squash=1.08, body_stretch=0.9, bounce=3, eye_scale=1.05,
                 expression="very_happy", duration=0.2),
    AnimKeyframe(body_squash=0.92, body_stretch=1.1, bounce=-8, eye_scale=1.1,
                 expression="very_happy", duration=0.2),
], loop=True)


def get_anim(name: str) -> AnimClip:
    return {
        "idle": ANIM_IDLE,
        "walk": ANIM_WALK,
        "sleep": ANIM_SLEEP,
        "eat": ANIM_EAT,
        "play": ANIM_PLAY,
        "happy": ANIM_HAPPY,
        "sad": ANIM_SAD,
        "curious": ANIM_CURIOUS,
        "surprised": ANIM_SURPRISED,
        "excited": ANIM_EXCITED,
        "mischievous": ANIM_MISCHIEVOUS,
        "dizzy": ANIM_DIZZY,
        "loving": ANIM_LOVING,
        "dance": ANIM_DANCE,
    }.get(name, ANIM_IDLE)
