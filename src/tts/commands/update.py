"""Update check and download command."""

import platform
import sys
import urllib.request
import json
from typing import Annotated

from cyclopts import Parameter

from tts import __version__

REPO = "guillempuche/text-to-speech"
RELEASES_API = f"https://api.github.com/repos/{REPO}/releases/latest"


def get_platform_binary() -> str:
    """Get the binary name for the current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        if machine in ("arm64", "aarch64"):
            return "tts-macos-arm64"
        return "tts-macos-x64"
    elif system == "linux":
        return "tts-linux-x64"
    elif system == "windows":
        return "tts-windows-x64.exe"
    else:
        return f"tts-{system}-{machine}"


def fetch_latest_release() -> dict | None:
    """Fetch latest release info from GitHub API."""
    try:
        req = urllib.request.Request(
            RELEASES_API,
            headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "tts-cli"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def parse_version(version: str) -> tuple:
    """Parse calver version string to comparable tuple."""
    # Remove 'v' prefix if present
    v = version.lstrip("v")
    # Split by dots and convert to integers
    parts = []
    for part in v.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def update(
    *,
    check: Annotated[
        bool, Parameter(name="--check", help="Only check for updates, don't show download instructions")
    ] = False,
) -> None:
    """Check for updates and show download instructions."""
    print(f"Current version: {__version__}")

    release = fetch_latest_release()
    if not release:
        print("\nCould not fetch release info from GitHub.")
        print(f"Check manually: https://github.com/{REPO}/releases")
        sys.exit(1)

    latest_tag = release.get("tag_name", "")
    latest_version = latest_tag.lstrip("v")

    print(f"Latest version:  {latest_version}")

    current = parse_version(__version__)
    latest = parse_version(latest_version)

    if current >= latest:
        print("\nYou're up to date!")
        return

    print(f"\nNew version available: {latest_version}")

    if check:
        return

    # Show download instructions
    binary_name = get_platform_binary()
    download_url = f"https://github.com/{REPO}/releases/download/{latest_tag}/{binary_name}"

    print(f"\nDownload for your platform ({platform.system()} {platform.machine()}):")
    print(f"  {download_url}")

    print("\nOr download manually:")
    print(f"  https://github.com/{REPO}/releases/tag/{latest_tag}")

    print("\nTo update:")
    if platform.system() == "Windows":
        print(f"  1. Download {binary_name}")
        print("  2. Replace your current tts.exe")
    else:
        print(f"  curl -L -o tts '{download_url}'")
        print("  chmod +x tts")
        print("  # Move to your preferred location")
