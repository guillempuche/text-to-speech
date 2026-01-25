"""Configure command for API key setup."""

import sys
from typing import Annotated

from cyclopts import Parameter

from tts.common import CONFIG_DIR, CREDENTIALS_FILE


def configure(
    api_key: Annotated[str, Parameter(help="Your Fish Audio API key")],
) -> None:
    """Save your Fish Audio API key for future use.

    Get your API key at: https://fish.audio
    """
    if not api_key.strip():
        print("Error: API key cannot be empty")
        sys.exit(1)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_FILE.write_text(f"FISH_API_KEY={api_key.strip()}\n")
    CREDENTIALS_FILE.chmod(0o600)

    print(f"API key saved to {CREDENTIALS_FILE}")
    print("You can now use tts commands without setting FISH_API_KEY.")
