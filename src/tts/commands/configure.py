"""Configure command for TTS CLI settings."""

import getpass
import sys
from pathlib import Path
from typing import Annotated, Literal

import cyclopts

from tts.common import (
    CONFIG_DIR,
    CREDENTIALS_FILE,
    _keyring_available,
    delete_api_key_from_keyring,
    get_api_key_from_keyring,
    set_api_key_in_keyring,
)
from tts.config import CONFIG_FILE, load_config, reset_config, update_config

app = cyclopts.App(
    name="configure",
    help="Configure TTS CLI settings.",
)


def _mask_key(key: str) -> str:
    """Mask API key for display, showing first 4 and last 4 chars."""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"


def _get_current_api_key() -> tuple[str | None, str]:
    """Get current API key and its source. Returns (key, source)."""
    import os

    # Check environment
    if key := os.environ.get("FISH_API_KEY"):
        return key, "environment variable"

    # Check keyring
    if key := get_api_key_from_keyring():
        return key, "keyring"

    # Check credentials file
    if CREDENTIALS_FILE.is_file():
        try:
            content = CREDENTIALS_FILE.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("FISH_API_KEY="):
                    key = line.partition("=")[2].strip().strip("\"'")
                    if key:
                        return key, f"credentials file ({CREDENTIALS_FILE})"
        except OSError:
            pass

    return None, "not configured"


@app.default
def configure_interactive(
    *,
    show: Annotated[
        bool, cyclopts.Parameter(name="--show", help="Show current configuration")
    ] = False,
    reset: Annotated[
        bool, cyclopts.Parameter(name="--reset", help="Reset to default configuration")
    ] = False,
) -> None:
    """Interactive configuration wizard.

    Run without arguments for interactive setup, or use subcommands for specific settings.
    """
    if show:
        _show_config()
        return

    if reset:
        _reset_all()
        return

    # Interactive wizard
    print("TTS CLI Configuration")
    print("=" * 40)
    print()

    # API Key
    api_key, source = _get_current_api_key()
    if api_key:
        print(f"API Key: {_mask_key(api_key)} (from {source})")
        response = input("Update API key? [y/N]: ").strip().lower()
        if response == "y":
            _prompt_and_save_api_key()
    else:
        print("API Key: not configured")
        _prompt_and_save_api_key()

    print()

    # Config settings
    config = load_config()
    print("Current settings:")
    print(f"  Default voice: {config.default_voice or '(not set)'}")
    print(f"  Output dir: {config.output_dir}")
    print(f"  Format: {config.format}")
    print(f"  Speed: {config.speed}")
    print()
    print("Use 'tts configure <setting> <value>' to update individual settings.")
    print("Use 'tts configure --show' to view full configuration.")


def _prompt_and_save_api_key() -> None:
    """Prompt for API key and save it."""
    print()
    print("Get your API key at: https://fish.audio")
    try:
        api_key = getpass.getpass("Enter API key: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return

    if not api_key:
        print("No key entered, skipping.")
        return

    # Try keyring first
    if set_api_key_in_keyring(api_key):
        print("API key saved to system keyring (secure storage).")
    else:
        # Fallback to credentials file
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CREDENTIALS_FILE.write_text(f"FISH_API_KEY={api_key}\n", encoding="utf-8")
        CREDENTIALS_FILE.chmod(0o600)
        print(f"API key saved to {CREDENTIALS_FILE}")


def _show_config() -> None:
    """Display current configuration."""
    print("TTS CLI Configuration")
    print("=" * 40)
    print()

    # API Key
    api_key, source = _get_current_api_key()
    if api_key:
        print(f"API Key: {_mask_key(api_key)}")
        print(f"  Source: {source}")
    else:
        print("API Key: not configured")

    print()

    # Config file settings
    config = load_config()
    print("Settings:")
    print(f"  default_voice: {config.default_voice or '(not set)'}")
    print(f"  output_dir: {config.output_dir}")
    print(f"  format: {config.format}")
    print(f"  speed: {config.speed}")

    print()
    print(f"Config file: {CONFIG_FILE}")
    print(f"Credentials: {CREDENTIALS_FILE}")
    if _keyring_available():
        print("Keyring: available")
    else:
        print("Keyring: not available")


def _reset_all() -> None:
    """Reset all configuration to defaults."""
    # Reset config file
    reset_config()
    print(f"Reset {CONFIG_FILE}")

    # Remove credentials file
    if CREDENTIALS_FILE.is_file():
        CREDENTIALS_FILE.unlink()
        print(f"Removed {CREDENTIALS_FILE}")

    # Remove from keyring
    if delete_api_key_from_keyring():
        print("Removed API key from keyring")

    print()
    print("Configuration reset to defaults.")


@app.command(name="api-key")
def configure_api_key(
    key: Annotated[
        str | None, cyclopts.Parameter(help="API key (omit for secure prompt)")
    ] = None,
) -> None:
    """Configure Fish Audio API key.

    If no key is provided, prompts securely without echo.
    """
    if key is None:
        print("Get your API key at: https://fish.audio")
        try:
            key = getpass.getpass("Enter API key: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            sys.exit(1)

    if not key.strip():
        print("Error: API key cannot be empty")
        sys.exit(1)

    key = key.strip()

    # Try keyring first
    if set_api_key_in_keyring(key):
        print("API key saved to system keyring (secure storage).")
    else:
        # Fallback to credentials file
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CREDENTIALS_FILE.write_text(f"FISH_API_KEY={key}\n", encoding="utf-8")
        CREDENTIALS_FILE.chmod(0o600)
        print(f"API key saved to {CREDENTIALS_FILE}")

    print("You can now use tts commands without setting FISH_API_KEY.")


@app.command(name="voice")
def configure_voice(
    voice_id: Annotated[str, cyclopts.Parameter(help="Default voice model ID")],
) -> None:
    """Set default voice model ID."""
    if not voice_id.strip():
        print("Error: Voice ID cannot be empty")
        sys.exit(1)

    update_config(default_voice=voice_id.strip())
    print(f"Default voice set to: {voice_id.strip()}")


@app.command(name="output-dir")
def configure_output_dir(
    path: Annotated[str, cyclopts.Parameter(help="Default output directory")],
) -> None:
    """Set default output directory."""
    if not path.strip():
        print("Error: Path cannot be empty")
        sys.exit(1)

    update_config(output_dir=path.strip())
    print(f"Default output directory set to: {path.strip()}")


@app.command(name="format")
def configure_format(
    fmt: Annotated[
        Literal["mp3", "wav", "pcm"], cyclopts.Parameter(help="Default audio format")
    ],
) -> None:
    """Set default audio format."""
    update_config(format=fmt)
    print(f"Default format set to: {fmt}")


@app.command(name="speed")
def configure_speed(
    value: Annotated[float, cyclopts.Parameter(help="Default speech speed (0.5-2.0)")],
) -> None:
    """Set default speech speed."""
    if not 0.5 <= value <= 2.0:
        print("Error: Speed must be between 0.5 and 2.0")
        sys.exit(1)

    update_config(speed=value)
    print(f"Default speed set to: {value}")


# Legacy support: direct API key argument for backward compatibility
def configure(api_key: str) -> None:
    """Legacy configure function for backward compatibility."""
    configure_api_key(api_key)
