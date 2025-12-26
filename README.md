# beatgrid

Elastic beatgrid CLI for variable tempo and vinyl drift handling. Wraps [QM-DSP/Vamp](https://vamp-plugins.org/).

## Features

- **Elastic Beatgrids** — Handle variable tempo
- **Vinyl Drift Correction** — Account for turntable speed variations
- **Beat Tracking** — Precise beat detection
- **Tempo Mapping** — Create tempo maps for variable-BPM tracks

## Installation

```bash
pip install beatgrid
```

## Usage

```bash
# Generate beatgrid
beatgrid analyze track.mp3

# Output tempo map
beatgrid analyze track.mp3 --format tempo-map
```

## Requirements

- Python 3.9+
- QM-DSP/Vamp plugins

## License

GPL-3.0 — See [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
