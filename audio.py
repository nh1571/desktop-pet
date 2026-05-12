"""Programmatic 8-bit style sound effects. No external audio files needed."""

import math
import struct

import pygame

SAMPLE_RATE = 22050


def _make_sine(freq, duration, volume=0.25, envelope=True):
    """Generate a sine wave sound."""
    n_samples = int(SAMPLE_RATE * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        amp = volume
        if envelope:
            # Quick fade in, longer fade out
            attack = min(1.0, i / (SAMPLE_RATE * 0.005))
            decay = max(0.0, 1.0 - i / n_samples)
            amp *= attack * decay
        sample = int(amp * 32767 * math.sin(2 * math.pi * freq * t))
        buf.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    return pygame.mixer.Sound(buffer=bytes(buf))


def _make_noise(duration, volume=0.15, envelope=True):
    """Generate white noise burst."""
    n_samples = int(SAMPLE_RATE * duration)
    buf = bytearray()
    import random
    for i in range(n_samples):
        amp = volume
        if envelope:
            decay = max(0.0, 1.0 - i / n_samples)
            amp *= decay
        sample = int(amp * 32767 * (random.random() * 2 - 1))
        buf.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    return pygame.mixer.Sound(buffer=bytes(buf))


def _make_sweep(start_freq, end_freq, duration, volume=0.25, envelope=True):
    """Generate a frequency sweep sound."""
    n_samples = int(SAMPLE_RATE * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        progress = i / n_samples
        freq = start_freq + (end_freq - start_freq) * progress
        amp = volume
        if envelope:
            decay = max(0.0, 1.0 - i / n_samples)
            amp *= decay
        sample = int(amp * 32767 * math.sin(2 * math.pi * freq * t))
        buf.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    return pygame.mixer.Sound(buffer=bytes(buf))


class SoundManager:
    def __init__(self):
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.muted = False
        self.volume = 0.3

    def init(self):
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        self.sounds = {
            "bloop": _make_sine(523, 0.12, 0.2),      # C5 chirp
            "nom": _make_noise(0.15, 0.12),            # eating munch
            "boing": _make_sweep(400, 800, 0.15, 0.2), # play bounce
            "yawn": _make_sine(180, 0.5, 0.18),        # sleep yawn
            "sad": _make_sweep(440, 220, 0.35, 0.18),  # descending whimper
            "happy": _make_sine(660, 0.1, 0.2),         # happy chime
            "step": _make_noise(0.03, 0.06),            # footstep squish
        }
        self._apply_volume()

    def play(self, name: str):
        if self.muted or name not in self.sounds:
            return
        self.sounds[name].play()

    def set_volume(self, vol: float):
        self.volume = max(0.0, min(1.0, vol))
        self._apply_volume()

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted

    def _apply_volume(self):
        for s in self.sounds.values():
            s.set_volume(self.volume)
