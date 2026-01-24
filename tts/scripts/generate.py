#!/usr/bin/env python3
"""Generate speech audio from text files using Fish Audio TTS."""

import os
import sys
from pathlib import Path
from typing import Annotated, Literal

try:
    import cyclopts
    from cyclopts import Parameter
except ImportError:
    print("Error: cyclopts not installed. Install with: pip install cyclopts")
    sys.exit(1)


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


def find_text_files(path: Path) -> list[Path]:
    """Find .txt files from a path (single file or directory)."""
    if path.is_file() and path.suffix == ".txt":
        return [path]
    if path.is_dir():
        try:
            entries = sorted(path.iterdir())
        except OSError as e:
            print(f"Error reading directory {path}: {e}")
            sys.exit(1)
        return [f for f in entries if f.suffix == ".txt" and f.is_file()]
    print(f"Error: {path} is not a .txt file or directory")
    sys.exit(1)


def main(
    input_path: Annotated[
        Path, Parameter(help="Directory of .txt files or a single .txt file")
    ],
    *,
    reference_id: Annotated[
        str, Parameter(name="--reference-id", help="Voice model ID for TTS")
    ],
    format: Annotated[
        Literal["mp3", "wav", "pcm"],
        Parameter(help="Output audio format"),
    ] = "mp3",
    speed: Annotated[float, Parameter(help="Speech speed (0.5-2.0)")] = 1.0,
    output_dir: Annotated[
        Path, Parameter(name="--output-dir", help="Output directory for audio files")
    ] = Path("./audio_output"),
    env_file: Annotated[
        Path | None, Parameter(name="--env-file", help="Path to .env file")
    ] = None,
) -> None:
    """Generate speech audio from text files using Fish Audio TTS."""
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

    if speed < 0.5 or speed > 2.0:
        print("Error: speed must be between 0.5 and 2.0")
        sys.exit(1)

    text_files = find_text_files(input_path)
    if not text_files:
        print(f"No .txt files found in {input_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Found {len(text_files)} text file(s)")
    print(f"Reference ID: {reference_id}")
    print(f"Format: {format}, Speed: {speed}")
    print(f"Output: {output_dir}\n")

    client = FishAudio()

    for txt_path in text_files:
        try:
            text = txt_path.read_text(encoding="utf-8").strip()
        except OSError as e:
            print(f"  Error reading {txt_path.name}: {e}")
            continue

        if not text:
            print(f"  Skipping {txt_path.name}: empty file")
            continue

        out_path = output_dir / f"{txt_path.stem}.{format}"
        print(f"  {txt_path.name} -> {out_path.name}")

        try:
            audio = client.tts.convert(
                text=text,
                reference_id=reference_id,
                format=format,
                speed=speed,
            )
            out_path.write_bytes(audio)
        except Exception as e:
            print(f"  Error generating {txt_path.name}: {e}")
            continue

    print("\nDone.")


if __name__ == "__main__":
    cyclopts.run(main)
