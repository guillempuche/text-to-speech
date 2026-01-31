"""Voice management commands."""

import subprocess
import sys
from pathlib import Path
from typing import Annotated, Literal

import cyclopts
from cyclopts import Parameter

from tts.common import get_fish_client, load_api_key

app = cyclopts.App(name="voice", help="Manage voice models.")

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}


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


@app.command
def upload(
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
    load_api_key(env_file)
    client = get_fish_client()

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


def _list_voices(env_file: Path | None = None) -> None:
    """Shared implementation for listing voice models."""
    load_api_key(env_file)
    client = get_fish_client()

    try:
        result = client.voices.list(self_only=True, page_size=100)
        if not result.items:
            print("No voice models found.")
            return

        print(f"Found {result.total} voice model(s):\n")
        for v in result.items:
            print(f"ID: {v.id}")
            print(f"  Title: {v.title}")
            if v.description:
                print(f"  Description: {v.description}")
            if hasattr(v, "visibility") and v.visibility:
                print(f"  Visibility: {v.visibility}")
            if hasattr(v, "languages") and v.languages:
                print(f"  Languages: {', '.join(v.languages)}")
            if hasattr(v, "tags") and v.tags:
                print(f"  Tags: {', '.join(v.tags)}")
            if hasattr(v, "state") and v.state:
                print(f"  State: {v.state}")
            if hasattr(v, "created_at") and v.created_at:
                print(f"  Created: {v.created_at}")
            print()
    except Exception as e:
        print(f"Error listing voices: {e}")
        sys.exit(1)


@app.command(name="list")
def list_voices(
    *,
    env_file: Annotated[
        Path | None, Parameter(name="--env-file", help="Path to .env file")
    ] = None,
) -> None:
    """List your voice models."""
    _list_voices(env_file)


@app.command
def list_models(
    *,
    env_file: Annotated[
        Path | None, Parameter(name="--env-file", help="Path to .env file")
    ] = None,
) -> None:
    """List your voice models (alias for 'list')."""
    _list_voices(env_file)
