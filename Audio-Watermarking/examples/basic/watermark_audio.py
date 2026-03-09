#!/usr/bin/env python
"""
Basic example of how to watermark an audio file using Perth.
"""
import os
import argparse
import numpy as np
import librosa
import soundfile as sf
from perth import PerthImplicitWatermarker
from perth.utils import calculate_audio_metrics

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Watermark an audio file with Perth")
    parser.add_argument("input_file", help="Path to the input audio file")
    parser.add_argument("--output", "-o", default=None,
                        help="Path to save the output watermarked audio file")
    parser.add_argument("--device", "-d", default="cpu", choices=["cpu", "cuda"],
                        help="Device to use for neural network processing")
    args = parser.parse_args()

    # Derive output filename if not specified
    if args.output is None:
        base, ext = os.path.splitext(args.input_file)
        args.output = f"{base}_watermarked{ext}"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    # Load audio file
    print(f"Loading audio file: {args.input_file}")
    wav, sr = librosa.load(args.input_file, sr=None)
    
    # Initialize watermarker
    print(f"Initializing Perth watermarker (device: {args.device})...")
    watermarker = PerthImplicitWatermarker(device=args.device)
    
    # Apply watermark
    print("Applying watermark...")
    watermarked_audio = watermarker.apply_watermark(wav, watermark=None, sample_rate=sr)
    
    # Save watermarked audio
    sf.write(args.output, watermarked_audio, sr)
    print(f"Watermarked audio saved to: {args.output}")
    
    # Check watermark in watermarked audio
    print("Verifying watermark...")
    extracted_watermark = watermarker.get_watermark(watermarked_audio, sample_rate=sr)
    print(f"Watermark verification confidence: {np.mean(extracted_watermark):.4f}")
    
    # Calculate quality metrics
    metrics = calculate_audio_metrics(wav, watermarked_audio)
    print("\nAudio Quality Metrics:")
    print(f"  Signal-to-Noise Ratio (SNR): {metrics['snr']:.2f} dB")
    print(f"  Mean Squared Error (MSE): {metrics['mse']:.6f}")
    print(f"  Peak Signal-to-Noise Ratio (PSNR): {metrics['psnr']:.2f} dB")


if __name__ == "__main__":
    main()