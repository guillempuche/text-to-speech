"""Shared utilities for TTS CLI."""

import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "tts"
CREDENTIALS_FILE = CONFIG_DIR / "credentials"

# Keyring configuration
KEYRING_SERVICE = "tts-cli"
KEYRING_USERNAME = "api-key"


def _keyring_available() -> bool:
    """Check if keyring is available and functional."""
    try:
        import keyring
        from keyring.errors import NoKeyringError

        # Test if a keyring backend is available
        keyring.get_keyring()
        return True
    except (ImportError, NoKeyringError):
        return False
    except Exception:
        return False


def get_api_key_from_keyring() -> str | None:
    """Get API key from system keyring."""
    if not _keyring_available():
        return None

    try:
        import keyring

        return keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except Exception:
        return None


def set_api_key_in_keyring(api_key: str) -> bool:
    """Store API key in system keyring. Returns True on success."""
    if not _keyring_available():
        return False

    try:
        import keyring

        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
        return True
    except Exception:
        return False


def delete_api_key_from_keyring() -> bool:
    """Delete API key from system keyring. Returns True on success."""
    if not _keyring_available():
        return False

    try:
        import keyring

        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        return True
    except Exception:
        return False


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


def load_api_key(env_file: Path | None = None) -> None:
    """Load FISH_API_KEY from various sources.

    Priority: env var -> keyring -> credentials file -> .env file
    """
    # Already set in environment
    if os.environ.get("FISH_API_KEY"):
        return

    # Try keyring
    keyring_key = get_api_key_from_keyring()
    if keyring_key:
        os.environ["FISH_API_KEY"] = keyring_key
        return

    # Try user config directory
    if CREDENTIALS_FILE.is_file():
        load_env_file(CREDENTIALS_FILE)
        if os.environ.get("FISH_API_KEY"):
            return

    # Try .env file
    env_path = env_file or Path(".env")
    if env_file:
        if not env_path.is_file():
            print(f"Error: env file not found: {env_path}")
            sys.exit(1)
        load_env_file(env_path)
    elif env_path.is_file():
        load_env_file(env_path)


def require_api_key() -> None:
    """Exit with error if FISH_API_KEY is not set."""
    if not os.environ.get("FISH_API_KEY"):
        print("Error: FISH_API_KEY not set.")
        print()
        print("Set it via:")
        print("  1. Run: tts configure api-key")
        print("  2. Or set environment variable: export FISH_API_KEY=<key>")
        print("  3. Or create .env file with: FISH_API_KEY=<key>")
        print()
        print("Get your API key at: https://fish.audio")
        sys.exit(1)


def get_fish_client():
    """Get Fish Audio client, exit if not available."""
    try:
        from fishaudio import FishAudio
    except ImportError:
        print("Error: fish-audio-sdk not installed.")
        sys.exit(1)

    require_api_key()
    return FishAudio()
