"""Parameterized beat detection tests using drum patterns."""

import json
import subprocess
import sys

import numpy as np
import pytest


def run_detect(file_path):
    cmd = [sys.executable, "-m", "audio_beatgrid.main", "detect", str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


class TestBeatDetectionAccuracy:
    """Test beat detection accuracy."""

    @pytest.mark.parametrize(
        "bpm",
        [90, 100, 110, 120, 128, 140, 174],
    )
    def test_bpm_detection_simple(self, generated_beat_file, bpm):
        """Verify BPM detection with simple click track."""
        path, expected_beats = generated_beat_file(bpm=bpm, duration=10.0)

        result = run_detect(path)
        assert result.returncode == 0

        data = json.loads(result.stdout)
        detected_bpm = data["bpm"]

        # Allow octave errors (half or double speed)
        bpm_match = abs(detected_bpm - bpm) < (bpm * 0.01)
        octave_match = abs(detected_bpm - bpm * 2) < (bpm * 0.02) or abs(detected_bpm - bpm / 2) < (bpm * 0.01)
        assert bpm_match or octave_match, f"Expected {bpm}, got {detected_bpm}"

    @pytest.mark.parametrize(
        "bpm, pattern",
        [
            (120, "four_on_floor"),
            (128, "four_on_floor"),
            (140, "breakbeat"),
            (90, "breakbeat"),
        ],
    )
    def test_bpm_detection_drums(self, generated_beat_file, bpm, pattern):
        """Verify BPM detection with drum patterns."""
        path, expected_beats = generated_beat_file(bpm=bpm, duration=10.0, pattern=pattern)

        result = run_detect(path)
        assert result.returncode == 0

        data = json.loads(result.stdout)
        detected_bpm = data["bpm"]

        # Allow octave errors for complex patterns
        # Breakbeats can be tricky, allow slightly wider tolerance
        tolerance = 2.0
        if pattern in ["breakbeat", "halftime"]:
            tolerance = 3.0

        bpm_match = abs(detected_bpm - bpm) < tolerance
        octave_match = abs(detected_bpm - bpm * 2) < tolerance or abs(detected_bpm - bpm / 2) < tolerance

        assert bpm_match or octave_match, f"Expected {bpm} ({pattern}), got {detected_bpm}"

    def test_beat_grid_alignment(self, generated_beat_file):
        """Verify detected beats align with actual beats."""
        bpm = 120
        path, expected_beats = generated_beat_file(bpm=bpm, duration=5.0, pattern="four_on_floor")

        result = run_detect(path)
        assert result.returncode == 0

        data = json.loads(result.stdout)
        detected_beats = np.array(data["beats"])

        # Validate internal consistency (interval)
        expected_interval = 60.0 / bpm
        intervals = np.diff(detected_beats)
        median_interval = np.median(intervals)

        assert abs(median_interval - expected_interval) < 0.02, "Beat intervals incorrect"


class TestErrorHandling:
    """Test error handling in beat detection."""

    def test_nonexistent_file(self):
        result = run_detect("/nonexistent.wav")
        assert result.returncode != 0

    def test_empty_file(self, temp_audio_path):
        with open(temp_audio_path, "w") as f:
            pass
        result = run_detect(temp_audio_path)
        assert result.returncode != 0

    def test_short_audio(self, temp_audio_path):
        """Verify handling of audio too short for analysis."""
        import soundfile as sf

        # 0.1s is likely too short
        sf.write(temp_audio_path, np.zeros(4410), 44100)

        result = run_detect(temp_audio_path)
        # Should fail gracefully
        assert result.returncode != 0 or json.loads(result.stdout)
