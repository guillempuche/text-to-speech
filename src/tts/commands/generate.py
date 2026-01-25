"""Generate speech audio from text files."""

import sys
from pathlib import Path
from typing import Annotated, Literal

from cyclopts import Parameter

from tts.common import get_fish_client, load_api_key


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


def generate(
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
    load_api_key(env_file)
    client = get_fish_client()

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
