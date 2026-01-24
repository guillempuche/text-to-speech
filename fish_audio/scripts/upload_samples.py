#!/usr/bin/env python3
"""Upload voice cloning samples to Fish Audio."""

import argparse
import os
import sys
from pathlib import Path

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg"}


def find_audio_files(directory: Path) -> list[Path]:
    """Find all audio files in the given directory."""
    files = []
    for f in sorted(directory.iterdir()):
        if f.suffix.lower() in AUDIO_EXTENSIONS and f.is_file():
            files.append(f)
    return files


def find_transcript(audio_path: Path) -> str | None:
    """Find a companion .txt transcript for an audio file."""
    txt_path = audio_path.with_suffix(".txt")
    if txt_path.exists():
        return txt_path.read_text().strip()
    return None


def upload_samples(
    directory: Path,
    title: str,
    description: str = "",
    enhance: bool = False,
) -> None:
    """Upload audio samples to Fish Audio to create a voice model."""
    try:
        from fish_audio_sdk import Session
    except ImportError:
        print("Error: fish-audio-sdk not installed.")
        print("Install with: pip install fish-audio-sdk")
        sys.exit(1)

    api_key = os.environ.get("FISH_AUDIO_API_KEY")
    if not api_key:
        print("Error: FISH_AUDIO_API_KEY environment variable not set.")
        sys.exit(1)

    audio_files = find_audio_files(directory)
    if not audio_files:
        print(f"No audio files found in {directory}")
        sys.exit(1)

    print(f"Found {len(audio_files)} audio file(s) in {directory}")

    session = Session(api_key)

    samples = []
    for audio_path in audio_files:
        transcript = find_transcript(audio_path)
        audio_bytes = audio_path.read_bytes()

        sample = {"audio": audio_bytes, "filename": audio_path.name}
        if transcript:
            sample["transcript"] = transcript
            print(f"  {audio_path.name} (with transcript)")
        else:
            print(f"  {audio_path.name}")

        samples.append(sample)

    print(f"\nCreating voice model: {title}")
    if description:
        print(f"Description: {description}")
    if enhance:
        print("Audio enhancement: enabled")

    try:
        model = session.voices.create(
            title=title,
            description=description,
            samples=samples,
            enhance=enhance,
        )
        print(f"\nVoice model created successfully!")
        print(f"Model ID: {model.id}")
    except Exception as e:
        print(f"\nError creating voice model: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Upload voice cloning samples to Fish Audio"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing audio samples",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Name for the voice model",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Description for the voice model",
    )
    parser.add_argument(
        "--enhance",
        action="store_true",
        help="Enable audio enhancement on samples",
    )

    args = parser.parse_args()

    if not args.directory.is_dir():
        print(f"Error: {args.directory} is not a directory")
        sys.exit(1)

    upload_samples(
        directory=args.directory,
        title=args.title,
        description=args.description,
        enhance=args.enhance,
    )


if __name__ == "__main__":
    main()
