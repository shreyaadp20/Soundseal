import os
import sys
import time
import numpy as np
import librosa
import soundfile as sf
import io
import contextlib
import gc

# ---------------- PATHS ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WATERMARK_DIR = os.path.join(BASE_DIR, "Audio-Watermarking", "src")
FINGERPRINT_DIR = os.path.join(BASE_DIR, "fingerprinting")

sys.path.append(WATERMARK_DIR)
sys.path.append(FINGERPRINT_DIR)

import perth
import audfprint

# ---------------- CONFIG ---------------- #
DATASET_FOLDER = os.path.join(FINGERPRINT_DIR, "music")
INPUT_FILE = os.path.join(DATASET_FOLDER, "blues.00000.wav")
OUTPUT_FILE = r"watermarked.wav"
DB_PATH = "integrated_fpdb.pklz"


def check_database():
    """Check DB integrity BEFORE any audfprint operations touch it."""
    if os.path.exists(DB_PATH):
        try:
            import gzip
            import pickle
            with gzip.open(DB_PATH, "rb") as f:
                pickle.load(f)
        except Exception:
            print("Corrupted fingerprint DB detected. Recreating...")
            # Force garbage collection to release any lingering file handles
            gc.collect()
            try:
                os.remove(DB_PATH)
                print("Corrupted DB removed. A fresh one will be created.")
            except PermissionError:
                print(
                    "WARNING: Could not delete corrupted DB — file is locked.\n"
                    f"Please manually delete '{DB_PATH}' and re-run the script."
                )
                sys.exit(1)


# ---------------- WATERMARKING ---------------- #

def apply_watermark(input_path, output_path):
    print("\n--- WATERMARKING ---")
    wav, sr = librosa.load(input_path, sr=None)

    watermarker = perth.DummyWatermarker()
    watermarked_audio = watermarker.apply_watermark(
        wav,
        watermark="IntegratedSystem",
        sample_rate=sr
    )

    sf.write(output_path, watermarked_audio, sr)
    print("Watermark applied and saved:", output_path)


def extract_watermark(file_path):
    wav, sr = librosa.load(file_path, sr=None)

    watermarker = perth.DummyWatermarker()
    watermark_data = watermarker.get_watermark(wav, sample_rate=sr)

    if isinstance(watermark_data, np.ndarray):
        watermark = "".join(map(str, watermark_data.astype(int).tolist()))
    else:
        watermark = str(watermark_data)

    print("Extracted Watermark:", watermark)
    return watermark


# ---------------- FINGERPRINTING ---------------- #

def add_to_fingerprint_db(db_path_or_file, file_path=None):
    print("\n--- ADDING TO FINGERPRINT DATABASE ---")

    # Support both calling conventions:
    #   add_to_fingerprint_db(file_path)            — old style
    #   add_to_fingerprint_db(db_path, file_path)   — new style (from app.py)
    if file_path is None:
        actual_db = DB_PATH
        actual_file = db_path_or_file
    else:
        actual_db = db_path_or_file
        actual_file = file_path

    cmd = "add" if os.path.exists(actual_db) else "new"
    args = ["audfprint", cmd, "--dbase", actual_db, actual_file]

    audfprint.main(args)

    # Give the OS a moment to fully flush and release the file handle
    time.sleep(0.5)

    print("Audio added to fingerprint database.")


def match_fingerprint(db_path_or_query, query_path=None):
    print("\n--- FINGERPRINT MATCHING ---")

    # Support both calling conventions:
    #   match_fingerprint(query_path)            — old style
    #   match_fingerprint(db_path, query_path)   — new style (from app.py)
    if query_path is None:
        actual_db = DB_PATH
        actual_query = db_path_or_query
    else:
        actual_db = db_path_or_query
        actual_query = query_path

    args = ["audfprint", "match", "--dbase", actual_db, actual_query]

    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        audfprint.main(args)

    output = f.getvalue()
    print(output)

    return "Matched" in output


# ---------------- METRICS ---------------- #

def watermark_detection_rate(folder):
    print("\n--- WATERMARK DETECTION RATE ---")

    total = 0
    detected = 0
    watermarker = perth.DummyWatermarker()

    for file in os.listdir(folder):
        if file.endswith(".wav"):
            total += 1
            path = os.path.join(folder, file)
            wav, sr = librosa.load(path, sr=None)
            watermark = watermarker.get_watermark(wav, sample_rate=sr)

            if isinstance(watermark, np.ndarray):
                if watermark.size > 0:
                    detected += 1
            elif watermark:
                detected += 1

    rate = detected / total if total > 0 else 0
    print("Detection Rate:", rate)
    return rate


def fingerprint_accuracy(folder):
    print("\n--- FINGERPRINT ACCURACY ---")

    total = 0
    correct = 0

    for file in os.listdir(folder):
        if file.endswith(".wav"):
            total += 1
            query = os.path.join(folder, file)
            result = match_fingerprint(query)
            if result:
                correct += 1

    accuracy = correct / total if total > 0 else 0
    print("Fingerprint Accuracy:", accuracy)
    return accuracy


def robustness_test(input_file):
    print("\n--- ROBUSTNESS TEST (NOISE ATTACK) ---")

    wav, sr = librosa.load(input_file, sr=None)
    noise = np.random.normal(0, 0.005, wav.shape)
    noisy_audio = wav + noise

    watermarker = perth.DummyWatermarker()
    watermark = watermarker.get_watermark(noisy_audio, sample_rate=sr)
    print("Watermark after noise attack:", watermark)


def processing_time(input_file):
    print("\n--- PROCESSING TIME ---")

    start = time.time()
    apply_watermark(input_file, OUTPUT_FILE)
    add_to_fingerprint_db(OUTPUT_FILE)
    end = time.time()

    print("Processing Time:", end - start, "seconds")


def overall_accuracy(folder):
    print("\n--- OVERALL SYSTEM ACCURACY ---")

    total = 0
    correct = 0

    for file in os.listdir(folder):
        if file.endswith(".wav"):
            total += 1
            path = os.path.join(folder, file)
            match = match_fingerprint(path)
            watermark = extract_watermark(path)
            if match and watermark is not None:
                correct += 1

    accuracy = correct / total if total > 0 else 0
    print("Overall Accuracy:", accuracy)
    return accuracy


# ---------------- MAIN PIPELINE ---------------- #

def main():
    print("\n====================================")
    print("INTEGRATED AUDIO WATERMARKING SYSTEM")
    print("====================================")

    # FIX: Check DB integrity FIRST, before audfprint opens it
    check_database()

    processing_time(INPUT_FILE)

    match_fingerprint(OUTPUT_FILE)

    extract_watermark(OUTPUT_FILE)

    watermark_detection_rate(DATASET_FOLDER)

    fingerprint_accuracy(DATASET_FOLDER)

    robustness_test(INPUT_FILE)

    overall_accuracy(DATASET_FOLDER)

    print("\n===== EVALUATION COMPLETE =====")


if __name__ == "__main__":
    main()