"""Shared test fixtures for audio-beatgrid tests."""

import os
import tempfile

import numpy as np
import pytest
import soundfile as sf

SAMPLE_RATE = 44100


def generate_kick(duration: float = 0.15) -> np.ndarray:
    """Generate a synthetic kick drum sound."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq_start = 150
    freq_end = 50
    freq = freq_start * np.exp(-t * 20) + freq_end
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    kick = np.sin(phase) * np.exp(-t * 15)
    return kick.astype(np.float32)


def generate_snare(duration: float = 0.1) -> np.ndarray:
    """Generate a synthetic snare drum sound."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 30)
    noise = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 20)
    snare = 0.5 * tone + 0.5 * noise
    return snare.astype(np.float32)


def generate_hihat(duration: float = 0.05) -> np.ndarray:
    """Generate a synthetic hi-hat sound."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 50)
    return noise.astype(np.float32)


def generate_drum_pattern(bpm: float, duration: float, pattern: str = "four_on_floor"):
    """Generate a drum pattern at the specified BPM.

    Returns:
        tuple: (audio_array, list_of_beat_times)
    """
    beat_duration = 60.0 / bpm
    total_samples = int(SAMPLE_RATE * duration)
    audio = np.zeros(total_samples, dtype=np.float32)

    kick = generate_kick()
    snare = generate_snare()
    hihat = generate_hihat()

    # Track expected beat locations (quarter notes)
    beat_times = []
    current_time = 0.0
    while current_time < duration:
        beat_times.append(current_time)
        current_time += beat_duration

    def place_sound(audio, sound, time_sec):
        start = int(time_sec * SAMPLE_RATE)
        end = min(start + len(sound), len(audio))
        if start < len(audio):
            audio[start:end] += sound[: end - start]

    beat_dur = 60.0 / bpm

    if pattern == "four_on_floor":
        current_time = 0.0
        beat = 0
        while current_time < duration:
            place_sound(audio, kick * 0.8, current_time)
            if beat % 4 in [1, 3]:  # Snare on 2 and 4
                place_sound(audio, snare * 0.6, current_time)
            place_sound(audio, hihat * 0.3, current_time)
            place_sound(audio, hihat * 0.2, current_time + beat_dur / 2)

            current_time += beat_dur
            beat += 1

    elif pattern == "breakbeat":
        current_time = 0.0
        while current_time < duration:
            place_sound(audio, kick * 0.8, current_time)
            place_sound(audio, kick * 0.6, current_time + beat_dur * 1.5)
            place_sound(audio, kick * 0.8, current_time + beat_dur * 2)
            place_sound(audio, snare * 0.6, current_time + beat_dur)
            place_sound(audio, snare * 0.6, current_time + beat_dur * 3)
            current_time += beat_dur * 4

    return audio, beat_times


def add_click_track(duration, bpm):
    """Legacy click track for backward compatibility."""
    bps = bpm / 60
    beat_interval = 1 / bps
    num_samples = int(SAMPLE_RATE * duration)
    audio = np.zeros(num_samples, dtype=np.float32)

    click_duration = 0.05
    click_freq = 1000
    click_t = np.linspace(0, click_duration, int(SAMPLE_RATE * click_duration), endpoint=False)
    click_wave = 0.8 * np.sin(2 * np.pi * click_freq * click_t) * np.exp(-10 * click_t)
    click_wave = click_wave.astype(np.float32)

    beats = np.arange(0, duration, beat_interval)
    real_beats = list(beats)

    for beat_time in beats:
        start_sample = int(beat_time * SAMPLE_RATE)
        end_sample = start_sample + len(click_wave)
        if end_sample < num_samples:
            audio[start_sample:end_sample] += click_wave

    return audio, real_beats


@pytest.fixture
def generated_beat_file():
    """Factory fixture to generate audio file with specific BPM/pattern."""
    files_to_clean = []

    def _create(bpm, duration=5.0, pattern=None):
        if pattern:
            audio, beats = generate_drum_pattern(bpm, duration, pattern)
        else:
            audio, beats = add_click_track(duration, bpm)

        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 0.001)

        fd, path = tempfile.mkstemp(suffix=f"_{bpm}bpm.wav")
        os.close(fd)

        sf.write(path, audio, SAMPLE_RATE)
        files_to_clean.append(path)
        return path, beats

    yield _create

    for p in files_to_clean:
        if os.path.exists(p):
            os.remove(p)


@pytest.fixture
def temp_audio_path():
    """Create a temporary file path for test audio."""
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)
