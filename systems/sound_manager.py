import array
import math
import pygame


def _make_tone(frequency, duration, volume=0.3, sample_rate=44100):
    """Sine wave with linear decay envelope, stereo 16-bit PCM."""
    n = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n):
        t = i / sample_rate
        env = max(0.0, 1.0 - t / duration)
        val = int(volume * 32767 * env * math.sin(2 * math.pi * frequency * t))
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


def _make_chirp(freq_start, freq_end, duration, volume=0.3, sample_rate=44100):
    """Linear frequency sweep, stereo 16-bit PCM."""
    n = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n):
        t = i / sample_rate
        freq = freq_start + (freq_end - freq_start) * (t / duration)
        val = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


class SoundManager:
    def __init__(self):
        self._gunshot = _make_tone(800, 0.06, volume=0.5)
        self._reload = _make_chirp(200, 500, 0.2, volume=0.3)
        self._hit = _make_tone(150, 0.10, volume=0.4)
        self._death = _make_chirp(400, 80, 0.6, volume=0.5)

    def play_gunshot(self):
        self._gunshot.play()

    def play_reload(self):
        self._reload.play()

    def play_hit(self):
        self._hit.play()

    def play_death(self):
        self._death.play()
