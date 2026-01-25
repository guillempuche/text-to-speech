"""Generate speech audio from text files."""

import sys
from pathlib import Path
from typing import Annotated, Literal

from cyclopts import Parameter

from tts.common import get_fish_client, load_api_key
from tts.config import load_config


def _is_glob_pattern(path_str: str) -> bool:
    """Check if a string contains glob pattern characters."""
    return any(c in path_str for c in ["*", "?", "["])


def find_text_files(path_or_pattern: Path | str) -> list[Path]:
    """Find .txt files from a path, directory, or glob pattern.

    Supports:
    - Single .txt file: /path/to/file.txt
    - Directory: /path/to/dir (finds all .txt files)
    - Glob patterns: "*.txt", "scripts/*.txt", "**/*.txt"
    """
    path_str = str(path_or_pattern)

    # Handle glob patterns
    if _is_glob_pattern(path_str):
        matches = sorted(Path.cwd().glob(path_str))
        # Filter to only .txt files
        return [f for f in matches if f.is_file() and f.suffix == ".txt"]

    # Handle regular paths
    path = Path(path_str) if isinstance(path_or_pattern, str) else path_or_pattern

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


def generate(
    input_path: Annotated[
        str, Parameter(help="Path, directory, or glob pattern (e.g., '*.txt', '**/*.txt')")
    ],
    *,
    reference_id: Annotated[
        str | None, Parameter(name="--reference-id", help="Voice model ID for TTS")
    ] = None,
    format: Annotated[
        Literal["mp3", "wav", "pcm"] | None,
        Parameter(help="Output audio format"),
    ] = None,
    speed: Annotated[float | None, Parameter(help="Speech speed (0.5-2.0)")] = None,
    output_dir: Annotated[
        Path | None,
        Parameter(name="--output-dir", help="Output directory for audio files"),
    ] = None,
    env_file: Annotated[
        Path | None, Parameter(name="--env-file", help="Path to .env file")
    ] = None,
) -> None:
    """Generate speech audio from text files using Fish Audio TTS.

    Supports glob patterns for batch processing:
      tts generate "*.txt"           # All .txt in current dir
      tts generate "scripts/*.txt"   # All .txt in scripts/
      tts generate "**/*.txt"        # Recursive search
    """
    load_api_key(env_file)
    client = get_fish_client()

    # Load config defaults
    config = load_config()

    # Apply config defaults for unspecified options
    effective_reference_id = reference_id or config.default_voice
    effective_format = format or config.format
    effective_speed = speed if speed is not None else config.speed
    effective_output_dir = output_dir or Path(config.output_dir)

    # Validate reference_id is provided
    if not effective_reference_id:
        print("Error: --reference-id is required (or set default with 'tts configure voice <id>')")
        sys.exit(1)

    if effective_speed < 0.5 or effective_speed > 2.0:
        print("Error: speed must be between 0.5 and 2.0")
        sys.exit(1)

    text_files = find_text_files(input_path)
    if not text_files:
        print(f"No .txt files found matching: {input_path}")
        sys.exit(1)

    effective_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Found {len(text_files)} text file(s)")
    print(f"Reference ID: {effective_reference_id}")
    print(f"Format: {effective_format}, Speed: {effective_speed}")
    print(f"Output: {effective_output_dir}\n")

    for txt_path in text_files:
        try:
            text = txt_path.read_text(encoding="utf-8").strip()
        except OSError as e:
            print(f"  Error reading {txt_path.name}: {e}")
            continue

        if not text:
            print(f"  Skipping {txt_path.name}: empty file")
            continue

        out_path = effective_output_dir / f"{txt_path.stem}.{effective_format}"
        print(f"  {txt_path.name} -> {out_path.name}")

        try:
            audio = client.tts.convert(
                text=text,
                reference_id=effective_reference_id,
                format=effective_format,
                speed=effective_speed,
            )
            out_path.write_bytes(audio)
        except Exception as e:
            print(f"  Error generating {txt_path.name}: {e}")
            continue

    print("\nDone.")
