import json
import logging
import sys
from pathlib import Path

import click
import numpy as np

# Configure logging to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(message)s")
logger = logging.getLogger("audio-beatgrid")


@click.group()
def cli():
    """Audio Beatgrid CLI using Essentia."""
    pass


@cli.command()
@click.argument("audio_path", type=click.Path(exists=True, path_type=Path))
def detect(audio_path: Path):
    """Detect beats and output JSON results."""
    try:
        import essentia.standard as es

        # Suppress warnings
        import warnings

        warnings.filterwarnings("ignore")

        # Load audio (use mono, 44.1kHz)
        # We use essentia's MonoLoader for simplicity and consistency with RhythmExtractor
        loader = es.MonoLoader(filename=str(audio_path), sampleRate=44100)
        audio = loader()

        # RhythmExtractor2013 is robust for electronic music
        # It returns: bpm, ticks (beats), confidence, estimates, bpmIntervals
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, beats, confidence, _, _ = rhythm_extractor(audio)

        # Convert to native python types for JSON
        result = {
            "beats": [float(b) for b in beats],  # Beats are timestamps in seconds
            "confidence": float(confidence),
            "bpm": float(bpm),
        }
        click.echo(json.dumps(result))

    except Exception as e:
        logger.error(f"Beat detection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
