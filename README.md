# Audio Beatgrid

[![CI](https://github.com/sohailbhamani/audio-beatgrid/actions/workflows/ci.yml/badge.svg)](https://github.com/sohailbhamani/audio-beatgrid/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A GPL-licensed CLI tool for extracting beat grids from audio files using Essentia. Perfect for DJ software and music production applications.

## Features

- **Beat Detection**: Precise beat position timestamps using Essentia's RhythmExtractor2013
- **BPM Extraction**: Accurate tempo detection
- **Confidence Score**: Beat detection confidence metric
- **JSON Output**: Clean JSON output for easy integration

## Installation

```bash
# Clone the repository
git clone https://github.com/sohailbhamani/audio-beatgrid.git
cd audio-beatgrid

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install --pre -e ".[dev]"
```

## Usage

```bash
# Detect beats in an audio file
audio-beatgrid detect path/to/song.mp3
```

### Output

```json
{
  "beats": [0.5, 1.0, 1.5, 2.0, 2.5, ...],
  "confidence": 0.87,
  "bpm": 128.0
}
```

## Development

```bash
# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## Dependencies

- [Essentia](https://essentia.upf.edu/) - Audio analysis library with beat detection
- [Click](https://click.palletsprojects.com/) - CLI framework

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
