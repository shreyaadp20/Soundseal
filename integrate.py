import os
import sys
import argparse

# Add paths to sys.path so we can import the modules
WATERMARK_DIR = r"c:\design_Projects\Audio-Watermarking\src"
FINGERPRINT_DIR = r"c:\design_Projects\fingerprinting"

if WATERMARK_DIR not in sys.path:
    sys.path.append(WATERMARK_DIR)
if FINGERPRINT_DIR not in sys.path:
    sys.path.append(FINGERPRINT_DIR)

try:
    import perth
    import librosa
    import soundfile as sf
except ImportError as e:
    print(f"Failed to import watermarking dependencies: {e}")
    sys.exit(1)

try:
    import audfprint
except ImportError as e:
    print(f"Failed to import fingerprinting dependencies: {e}")
    sys.exit(1)

def apply_watermark(input_path, output_path):
    print(f"Applying watermark to {input_path}...")
    wav, sr = librosa.load(input_path, sr=None)
    # Using DummyWatermarker here for demonstration, you can switch to PerthImplicitWatermarker
    # watermarker = perth.PerthImplicitWatermarker() 
    watermarker = perth.DummyWatermarker()
    watermarked_audio = watermarker.apply_watermark(wav, watermark="IntegratedSystem", sample_rate=sr)
    sf.write(output_path, watermarked_audio, sr)
    print(f"Watermarked audio saved to {output_path}")

def extract_watermark(input_path):
    print(f"Extracting watermark from {input_path}...")
    try:
        wav, sr = librosa.load(input_path, sr=None)
        watermarker = perth.DummyWatermarker()
        watermark = watermarker.get_watermark(wav, sample_rate=sr)
        print(f"Extracted watermark: {watermark}")
        return watermark
    except Exception as e:
        print(f"Error extracting watermark: {e}")
        return None

def add_to_fingerprint_db(db_path, file_path):
    print(f"Adding {file_path} to fingerprint database {db_path}...")
    import os
    cmd = "add" if os.path.exists(db_path) else "new"
    args = ["audfprint", cmd, "--dbase", db_path, file_path]
    audfprint.main(args)
    print("Added to the database.")

def match_fingerprint(db_path, query_path):
    print(f"Matching {query_path} against fingerprint database {db_path}...")
    args = ["audfprint", "match", "--dbase", db_path, query_path]
    audfprint.main(args)

def main():
    parser = argparse.ArgumentParser(description="Integrated Audio Watermarking and Fingerprinting")
    subparsers = parser.add_subparsers(dest="command")

    # Command: ingest (Watermark + Fingerprint)
    ingest_parser = subparsers.add_parser("ingest", help="Watermark an audio file and add it to fingerprint DB")
    ingest_parser.add_argument("input_wav", help="Input audio file")
    ingest_parser.add_argument("output_wav", help="Path to save the watermarked audio")
    ingest_parser.add_argument("--dbase", default="integrated_fpdb.pklz", help="Fingerprint DB file")

    # Command: verify (Match + Extract Watermark)
    verify_parser = subparsers.add_parser("verify", help="Identify an audio file and extract its watermark")
    verify_parser.add_argument("query_wav", help="Audio file to verify")
    verify_parser.add_argument("--dbase", default="integrated_fpdb.pklz", help="Fingerprint DB file")

    args = parser.parse_args()

    if args.command == "ingest":
        apply_watermark(args.input_wav, args.output_wav)
        add_to_fingerprint_db(args.dbase, args.output_wav)
        print("Ingestion complete.")
    elif args.command == "verify":
        match_fingerprint(args.dbase, args.query_wav)
        extract_watermark(args.query_wav)
        print("Verification complete.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
