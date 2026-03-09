# Perth API Reference

This document provides detailed information about the classes and functions available in the Perth library.

## Core Classes

### WatermarkerBase

`WatermarkerBase` is the abstract base class that all watermarking implementations in Perth extend.

```python
from perth import WatermarkerBase
```

#### Methods

- **apply_watermark**(wav, watermark=None, sample_rate=44100, **kwargs)
  
  Apply a watermark to an audio signal.
  
  - **Parameters**:
    - `wav` (np.ndarray): Input audio signal as numpy array
    - `watermark` (np.ndarray, optional): Watermark data to embed. If None, a default watermark is generated.
    - `sample_rate` (int): Sample rate of the audio signal in Hz
    - `**kwargs`: Additional algorithm-specific parameters
  
  - **Returns**:
    - `np.ndarray`: Watermarked audio signal

- **get_watermark**(watermarked_wav, sample_rate=44100, watermark_length=None, **kwargs)
  
  Extract a watermark from a watermarked audio signal.
  
  - **Parameters**:
    - `watermarked_wav` (np.ndarray): Watermarked audio signal
    - `sample_rate` (int): Sample rate of the audio signal in Hz
    - `watermark_length` (int, optional): Expected length of the watermark
    - `**kwargs`: Additional algorithm-specific parameters
  
  - **Returns**:
    - `np.ndarray`: Extracted watermark data

### PerthImplicitWatermarker

`PerthImplicitWatermarker` is a neural network-based watermarking implementation that uses the Perth-Net model for embedding and extracting watermarks.

```python
from perth import PerthImplicitWatermarker
```

#### Constructor

- **\_\_init\_\_**(run_name="implicit", models_dir=None, device="cpu", perth_net=None)
  
  - **Parameters**:
    - `run_name` (str): Name of the model configuration to load
    - `models_dir` (str, optional): Directory containing the model files
    - `device` (str): Device to run the model on ("cpu" or "cuda")
    - `perth_net` (PerthNet, optional): Pre-initialized PerthNet model instance

#### Methods

Inherits all methods from `WatermarkerBase` with the following implementations:

- **apply_watermark**(signal, watermark, sample_rate, **_)
  
  Apply a neural network-based watermark to an audio signal.
  
  - **Parameters**:
    - `signal` (np.ndarray): Input audio signal
    - `watermark` (np.ndarray, optional): Ignored (Perth-Net generates its own watermark)
    - `sample_rate` (int): Sample rate of the audio signal in Hz
  
  - **Returns**:
    - `np.ndarray`: Watermarked audio signal

- **get_watermark**(wm_signal, sample_rate, round=True, **_)
  
  Extract a watermark from a watermarked audio signal.
  
  - **Parameters**:
    - `wm_signal` (np.ndarray): Watermarked audio signal
    - `sample_rate` (int): Sample rate of the audio signal in Hz
    - `round` (bool): Whether to round the watermark values to binary (0 or 1)
  
  - **Returns**:
    - `np.ndarray`: Extracted watermark data

## Utility Functions

### Audio Processing

```python
from perth.utils import load_audio, save_audio
```

- **load_audio**(audio_path, sr=None)
  
  Load an audio file using librosa.
  
  - **Parameters**:
    - `audio_path` (str): Path to the audio file
    - `sr` (int, optional): Target sample rate. If None, the native sample rate is used.
  
  - **Returns**:
    - `tuple`: (audio_data, sample_rate)

- **save_audio**(audio_data, file_path, sample_rate)
  
  Save audio data to a file.
  
  - **Parameters**:
    - `audio_data` (np.ndarray): Audio data as a numpy array
    - `file_path` (str): Output file path
    - `sample_rate` (int): Sample rate for the audio file

### Analysis and Visualization

```python
from perth.utils import calculate_audio_metrics, plot_audio_comparison
```

- **calculate_audio_metrics**(original, watermarked)
  
  Calculate audio quality metrics between original and watermarked audio.
  
  - **Parameters**:
    - `original` (np.ndarray): Original audio data
    - `watermarked` (np.ndarray): Watermarked audio data
  
  - **Returns**:
    - `dict`: Dictionary with quality metrics:
      - `snr`: Signal-to-Noise Ratio (dB)
      - `mse`: Mean Squared Error
      - `psnr`: Peak Signal-to-Noise Ratio (dB)

- **plot_audio_comparison**(original, watermarked, sample_rate, output_path=None)
  
  Plot a comparison between original and watermarked audio.
  
  - **Parameters**:
    - `original` (np.ndarray): Original audio data
    - `watermarked` (np.ndarray): Watermarked audio data
    - `sample_rate` (int): Sample rate of the audio
    - `output_path` (str, optional): Path to save the plot. If None, plot is shown interactively.

## Command Line Interface

perth provides a command-line interface through the `perth` command:

```
perth [OPTIONS] INPUT_FILE
```

### Options

- `--output`, `-o`: Path to save the output watermarked audio file
- `--method`, `-m`: Watermarking method to use (choices: perth, dummy)
- `--extract`, `-e`: Extract watermark from the input file instead of applying a watermark
- `--device`, `-d`: Device to use for neural network processing (choices: cpu, cuda)
