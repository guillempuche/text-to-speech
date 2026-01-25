"""Configuration management for TTS CLI."""

import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Literal

CONFIG_DIR = Path.home() / ".config" / "tts"
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class TTSConfig:
    """TTS CLI configuration."""

    default_voice: str | None = None
    output_dir: str = "./audio_output"
    format: Literal["mp3", "wav", "pcm"] = "mp3"
    speed: float = 1.0

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.format not in ("mp3", "wav", "pcm"):
            raise ValueError(f"Invalid format: {self.format}")
        if not 0.5 <= self.speed <= 2.0:
            raise ValueError(f"Speed must be between 0.5 and 2.0: {self.speed}")


def load_config() -> TTSConfig:
    """Load configuration from file, returning defaults if not found."""
    if not CONFIG_FILE.is_file():
        return TTSConfig()

    try:
        content = CONFIG_FILE.read_text(encoding="utf-8")
        data = tomllib.loads(content)
    except (OSError, tomllib.TOMLDecodeError):
        return TTSConfig()

    # Extract only known fields
    valid_fields = {f.name for f in fields(TTSConfig)}
    filtered = {k: v for k, v in data.items() if k in valid_fields}

    try:
        return TTSConfig(**filtered)
    except (TypeError, ValueError):
        return TTSConfig()


def save_config(config: TTSConfig) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    if config.default_voice is not None:
        lines.append(f'default_voice = "{config.default_voice}"')
    lines.append(f'output_dir = "{config.output_dir}"')
    lines.append(f'format = "{config.format}"')
    lines.append(f"speed = {config.speed}")

    CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_config(**kwargs) -> TTSConfig:
    """Update specific config values and save."""
    config = load_config()

    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    # Validate the updated config
    config.__post_init__()
    save_config(config)
    return config


def reset_config() -> TTSConfig:
    """Reset configuration to defaults."""
    config = TTSConfig()
    save_config(config)
    return config
