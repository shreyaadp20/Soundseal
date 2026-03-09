# Getting Started with Perth

This guide will help you get started with the Perth audio watermarking library.

## Installation

### Prerequisites

Before installing Perth, make sure you have the following prerequisites:

- Python 3.8 or higher
- pip package manager

For GPU acceleration (optional):
- CUDA-compatible GPU
- PyTorch with CUDA support

### Install from PyPI

```bash
pip install resemble-perth
```

### Install from Source

```bash
git clone https://github.com/resemble-ai/Perth
cd Perth
pip install -e .
```

## Basic Usage

Here's a simple example of how to use Perth to watermark an audio file:

```python
import librosa
import soundfile as sf
from perth import PerthImplicitWatermarker

# Load audio file
audio, sample_rate = librosa.load('input.wav', sr=None)

# Initialize watermarker
watermarker = PerthImplicitWatermarker()

# Apply watermark
watermarked_audio = watermarker.apply_watermark(audio, sample_rate=sample_rate)

# Save watermarked audio
sf.write('output.wav', watermarked_audio, sample_rate)
```

To extract a watermark from an audio file:

```python
import librosa
from perth import PerthImplicitWatermarker

# Load audio file
audio, sample_rate = librosa.load('output.wav', sr=None)

# Initialize watermarker
watermarker = PerthImplicitWatermarker()

# Extract watermark
watermark = watermarker.get_watermark(audio, sample_rate=sample_rate)
print(f"Extracted watermark confidence: {watermark.mean():.4f}")
```

## Command Line Usage

Perth also provides a command-line interface for easy usage:

```bash
# Watermark an audio file
perth input.wav -o output.wav

# Extract a watermark from a file
perth input.wav --extract
```

Run `perth --help` for more options and information.

## Next Steps

- Check out the [examples](../examples/) directory for more complex usage examples
- See the [API Reference](./api_reference.md) for detailed information on available functions and classes
- Learn about [watermarking techniques](./watermarking_techniques.md) implemented in Perth