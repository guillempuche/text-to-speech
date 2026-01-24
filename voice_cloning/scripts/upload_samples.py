#!/usr/bin/env python3
"""Upload voice cloning samples to Fish Audio."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Literal

try:
    import cyclopts
    from cyclopts import Parameter
except ImportError:
    print("Error: cyclopts not installed. Install with: pip install cyclopts")
    sys.exit(1)

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE pairs from a file into os.environ (won't override existing)."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Error: could not read env file {path}: {e}")
        sys.exit(1)

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value


def find_audio_files(directory: Path) -> list[Path]:
    """Find all audio files in the given directory."""
    try:
        entries = sorted(directory.iterdir())
    except OSError as e:
        print(f"Error reading directory {directory}: {e}")
        sys.exit(1)

    return [f for f in entries if f.suffix.lower() in AUDIO_EXTENSIONS and f.is_file()]


def convert_to_wav(audio_path: Path) -> bytes:
    """Convert an audio file to WAV (PCM 16-bit) via ffmpeg, return wav bytes."""
    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(audio_path),
            "-f",
            "wav",
            "-acodec",
            "pcm_s16le",
            "pipe:1",
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode().strip().splitlines()[-1])
    return result.stdout


def read_transcript(audio_path: Path) -> str | None:
    """Read a companion .txt transcript matching the audio file stem."""
    txt_path = audio_path.with_suffix(".txt")
    if not txt_path.exists():
        return None
    try:
        content = txt_path.read_text(encoding="utf-8").strip()
    except OSError as e:
        print(f"  Warning: could not read {txt_path.name}: {e}")
        return None
    if not content:
        print(f"  Warning: {txt_path.name} is empty, skipping transcript")
        return None
    return content


def main(
    directory: Annotated[Path, Parameter(help="Directory containing audio samples")],
    *,
    title: Annotated[str, Parameter(help="Name for the voice model")],
    description: Annotated[str, Parameter(help="Description for the voice model")] = "",
    enhance: Annotated[
        bool, Parameter(help="Enable audio quality enhancement")
    ] = False,
    visibility: Annotated[
        Literal["private", "public", "unlist"],
        Parameter(help="Voice model visibility"),
    ] = "private",
    tags: Annotated[
        list[str] | None, Parameter(help="Tags for the voice model")
    ] = None,
    env_file: Annotated[
        Path | None, Parameter(name="--env-file", help="Path to .env file")
    ] = None,
) -> None:
    """Upload voice cloning samples to Fish Audio."""
    # Load .env
    env_path = env_file or Path(".env")
    if env_file:
        if not env_path.is_file():
            print(f"Error: env file not found: {env_path}")
            sys.exit(1)
        load_env_file(env_path)
    elif env_path.is_file():
        load_env_file(env_path)

    try:
        from fishaudio import FishAudio
    except ImportError:
        print("Error: fishaudio not installed. Install with: pip install fishaudio")
        sys.exit(1)

    if not os.environ.get("FISH_API_KEY"):
        print("Error: FISH_API_KEY environment variable not set.")
        sys.exit(1)

    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        sys.exit(1)

    audio_files = find_audio_files(directory)
    if not audio_files:
        print(f"No audio files found in {directory}")
        sys.exit(1)

    print(f"Found {len(audio_files)} audio file(s) in {directory}")

    voices: list[bytes] = []
    texts: list[str] = []
    all_have_transcripts = True
    errors: list[str] = []

    for audio_path in audio_files:
        try:
            if audio_path.suffix.lower() == ".wav":
                audio_bytes = audio_path.read_bytes()
            else:
                audio_bytes = convert_to_wav(audio_path)
        except (OSError, RuntimeError) as e:
            errors.append(f"  Could not read {audio_path.name}: {e}")
            continue

        if not audio_bytes:
            errors.append(f"  {audio_path.name} is empty, skipping")
            continue

        transcript = read_transcript(audio_path)
        voices.append(audio_bytes)

        if transcript:
            texts.append(transcript)
            print(f"  {audio_path.name} -> {audio_path.stem}.txt")
        else:
            all_have_transcripts = False
            print(f"  {audio_path.name}")

    if errors:
        print("\nSkipped files:")
        for err in errors:
            print(err)

    if not voices:
        print("\nError: no valid audio files to upload.")
        sys.exit(1)

    if texts and not all_have_transcripts:
        print("\nWarning: some files have transcripts and some don't.")
        print(
            "Provide transcripts for ALL files or none. Ignoring partial transcripts."
        )
        texts = []

    print(f"\nCreating voice model: {title}")
    if description:
        print(f"Description: {description}")
    if enhance:
        print("Audio enhancement: enabled")
    print(f"Visibility: {visibility}")

    client = FishAudio()

    create_kwargs: dict = {
        "title": title,
        "voices": voices,
        "description": description,
        "enhance_audio_quality": enhance,
        "visibility": visibility,
    }
    if texts:
        create_kwargs["texts"] = texts
    if tags:
        create_kwargs["tags"] = tags

    try:
        voice = client.voices.create(**create_kwargs)
        print(f"\nVoice model created: {voice.id}")
    except Exception as e:
        print(f"\nError creating voice model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cyclopts.run(main)
