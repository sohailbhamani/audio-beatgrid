import os
import tempfile

import numpy as np
import pytest
import soundfile as sf

SAMPLE_RATE = 44100


def add_click_track(duration, bpm):
    bps = bpm / 60
    beat_interval = 1 / bps
    num_samples = int(SAMPLE_RATE * duration)
    audio = np.zeros(num_samples)

    click_duration = 0.05
    click_freq = 1000
    click_t = np.linspace(
        0, click_duration, int(SAMPLE_RATE * click_duration), endpoint=False
    )
    click_wave = 0.8 * np.sin(2 * np.pi * click_freq * click_t) * np.exp(-10 * click_t)

    beats = np.arange(0, duration, beat_interval)
    real_beats = []

    for beat_time in beats:
        start_sample = int(beat_time * SAMPLE_RATE)
        end_sample = start_sample + len(click_wave)
        if end_sample < num_samples:
            audio[start_sample:end_sample] += click_wave
            real_beats.append(beat_time)

    return audio, real_beats


@pytest.fixture
def generated_beat_file():
    """Factory fixture to generate audio file with specific BPM."""
    files_to_clean = []

    def _create(bpm, duration=5.0):
        audio, beats = add_click_track(duration, bpm)

        fd, path = tempfile.mkstemp(suffix=f"_{bpm}bpm.wav")
        os.close(fd)

        sf.write(path, audio, SAMPLE_RATE)
        files_to_clean.append(path)
        return path, beats

    yield _create

    for p in files_to_clean:
        if os.path.exists(p):
            os.remove(p)
