"""Update check and auto-update command."""

import hashlib
import platform
import shutil
import stat
import sys
import tempfile
import urllib.request
import json
from pathlib import Path
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
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "tts-cli",
            },
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


def get_binary_path() -> Path | None:
    """Get the path to the running binary.

    Returns None if not running as a PyApp binary (e.g., running via pip install).
    """
    import os

    # PyApp sets PYAPP=1 when running as a binary
    if not os.environ.get("PYAPP"):
        return None

    # sys.executable points to the binary itself when running via PyApp
    return Path(sys.executable)


def download_file(url: str, dest: Path, show_progress: bool = True) -> None:
    """Download a file from URL to destination with optional progress."""
    req = urllib.request.Request(url, headers={"User-Agent": "tts-cli"})

    with urllib.request.urlopen(req, timeout=60) as response:
        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        block_size = 8192

        with open(dest, "wb") as f:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                f.write(buffer)

                if show_progress and total_size > 0:
                    percent = downloaded * 100 // total_size
                    bar = "=" * (percent // 2) + " " * (50 - percent // 2)
                    print(f"\r  [{bar}] {percent}%", end="", flush=True)

        if show_progress:
            print()  # Newline after progress bar


def fetch_checksums(tag: str) -> dict[str, str]:
    """Fetch and parse checksums.txt from a GitHub release.

    Returns dict mapping filename to sha256 hash.
    """
    url = f"https://github.com/{REPO}/releases/download/{tag}/checksums.txt"
    req = urllib.request.Request(url, headers={"User-Agent": "tts-cli"})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode()
    except Exception:
        return {}

    checksums = {}
    for line in content.strip().split("\n"):
        if line and "  " in line:
            # Format: "hash  filename"
            parts = line.split("  ", 1)
            if len(parts) == 2:
                checksum, filename = parts
                checksums[filename.strip()] = checksum.strip()

    return checksums


def verify_checksum(file_path: Path, expected: str) -> bool:
    """Verify SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected


def cleanup_old_binary() -> None:
    """Remove .old backup file from previous update (Windows)."""
    binary_path = get_binary_path()
    if binary_path:
        old_path = binary_path.with_suffix(binary_path.suffix + ".old")
        if old_path.exists():
            try:
                old_path.unlink()
            except Exception:
                pass


def update(
    *,
    check: Annotated[
        bool, Parameter(name="--check", help="Only check for updates, don't download")
    ] = False,
    force: Annotated[
        bool, Parameter(name="--force", help="Update without confirmation prompt")
    ] = False,
) -> None:
    """Check for updates and auto-update if running as binary."""
    # Clean up old binary from previous update (Windows)
    if platform.system() == "Windows":
        cleanup_old_binary()

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

    # Detect if running as binary
    binary_path = get_binary_path()

    if not binary_path:
        # Running via pip install
        print("\nTo update, run:")
        print("  pip install --upgrade text-to-speech")
        print(
            f"\nOr download binary: https://github.com/{REPO}/releases/tag/{latest_tag}"
        )
        return

    # Auto-update binary
    binary_name = get_platform_binary()
    download_url = (
        f"https://github.com/{REPO}/releases/download/{latest_tag}/{binary_name}"
    )

    # Confirm with user unless --force
    if not force:
        print(f"\nReady to update: {binary_path}")
        try:
            response = input("Proceed with update? [Y/n] ").strip().lower()
            if response and response not in ("y", "yes"):
                print("Update cancelled.")
                return
        except (KeyboardInterrupt, EOFError):
            print("\nUpdate cancelled.")
            return

    # Fetch checksums
    print("\nFetching checksums...")
    checksums = fetch_checksums(latest_tag)
    expected_checksum = checksums.get(binary_name)

    if not expected_checksum:
        print(f"Warning: No checksum found for {binary_name}")
        if not force:
            try:
                response = (
                    input("Continue without verification? [y/N] ").strip().lower()
                )
                if response not in ("y", "yes"):
                    print("Update cancelled.")
                    return
            except (KeyboardInterrupt, EOFError):
                print("\nUpdate cancelled.")
                return

    # Download to temp file
    print(f"Downloading {binary_name}...")
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(binary_name).suffix
    ) as tmp:
        tmp_path = Path(tmp.name)

    try:
        download_file(download_url, tmp_path)
    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        print(f"\nDownload failed: {e}")
        sys.exit(1)

    # Verify checksum
    if expected_checksum:
        print("Verifying checksum...")
        if not verify_checksum(tmp_path, expected_checksum):
            tmp_path.unlink()
            print("Checksum verification failed! Update aborted.")
            sys.exit(1)
        print("Checksum verified.")

    # Replace binary
    print("Installing update...")
    try:
        if platform.system() == "Windows":
            # Windows: Can't replace running binary, rename to .old first
            old_path = binary_path.with_suffix(binary_path.suffix + ".old")
            if old_path.exists():
                old_path.unlink()
            binary_path.rename(old_path)
            shutil.move(str(tmp_path), str(binary_path))
        else:
            # Unix: Can replace running binary directly
            # Make executable before moving
            tmp_path.chmod(
                tmp_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            )
            shutil.move(str(tmp_path), str(binary_path))
    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        print(f"\nFailed to install update: {e}")
        sys.exit(1)

    print(f"\nSuccessfully updated to {latest_version}!")
    print("Run 'tts --version' to verify.")
