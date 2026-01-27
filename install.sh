#!/bin/bash
#
# Text-to-Speech CLI Installer
# https://github.com/guillempuche/text-to-speech
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/guillempuche/text-to-speech/main/install.sh | bash
#
# Environment variables:
#   TTS_INSTALL_DIR - Installation directory (default: /usr/local/bin)
#   TTS_VERSION     - Specific version to install (default: latest)
#

# -e: Exit on error | -u: Error on undefined vars | -o pipefail: Catch pipe failures
# Best practice: Always use strict mode to catch errors early
set -euo pipefail

# Configuration constants
REPO="guillempuche/text-to-speech"
GITHUB_URL="https://github.com/$REPO"
BINARY_NAME="tts"
DEFAULT_INSTALL_DIR="/usr/local/bin"  # Standard location for user-installed binaries

# Allow user override via environment variable
# Best practice: Make scripts configurable without modification
INSTALL_DIR="${TTS_INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"

# Terminal colors - disabled when output is piped (not a TTY)
# Best practice: Check if terminal supports colors before using them
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'  # No Color - reset
else
    RED='' GREEN='' YELLOW='' NC=''
fi

# Logging functions with consistent prefixes
info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }  # Errors go to stderr

# Cleanup handler - runs on script exit (success or failure)
# Best practice: Always clean up temporary files to avoid disk pollution
TMP_DIR=""
cleanup() {
    if [ -n "$TMP_DIR" ] && [ -d "$TMP_DIR" ]; then
        rm -rf "$TMP_DIR"
    fi
}
trap cleanup EXIT  # Register cleanup to run on any exit

# Detect operating system using uname
# Best practice: Use portable commands that work across Unix systems
detect_os() {
    local os
    os="$(uname -s)"
    case "$os" in
        Linux*)  echo "linux" ;;
        Darwin*) echo "macos" ;;
        MINGW*|MSYS*|CYGWIN*)  # Windows environments
            error "Windows detected. Please use the PowerShell installer instead:
  irm https://raw.githubusercontent.com/$REPO/main/install.ps1 | iex"
            ;;
        *) error "Unsupported operating system: $os" ;;
    esac
}

# Detect CPU architecture
# Best practice: Support both x64 and ARM64 for modern hardware
detect_arch() {
    local arch
    arch="$(uname -m)"
    case "$arch" in
        x86_64|amd64)   echo "x64" ;;    # Intel/AMD 64-bit
        arm64|aarch64)  echo "arm64" ;;  # Apple Silicon, ARM servers
        *) error "Unsupported architecture: $arch" ;;
    esac
}

# Fetch latest version tag from GitHub API
# Best practice: Use API instead of scraping HTML pages
get_latest_version() {
    local version
    # GitHub API returns JSON; extract tag_name field
    version=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
        | grep '"tag_name"' \
        | sed -E 's/.*"([^"]+)".*/\1/')

    if [ -z "$version" ]; then
        error "Failed to fetch latest version from GitHub"
    fi
    echo "$version"
}

# Map OS/arch to binary filename
get_binary_name() {
    local os="$1"
    local arch="$2"

    case "$os" in
        linux)
            # Linux ARM64 not yet supported - would need cross-compilation
            if [ "$arch" = "arm64" ]; then
                error "Linux ARM64 is not currently supported. Please build from source."
            fi
            echo "tts-linux-x64"
            ;;
        macos)
            echo "tts-macos-$arch"  # tts-macos-x64 or tts-macos-arm64
            ;;
    esac
}

# Verify SHA256 checksum of downloaded file
# Best practice: Always verify downloads to detect corruption or tampering
verify_checksum() {
    local file="$1"
    local expected="$2"
    local actual

    # macOS uses 'shasum', Linux uses 'sha256sum'
    if command -v sha256sum &> /dev/null; then
        actual=$(sha256sum "$file" | cut -d' ' -f1)
    elif command -v shasum &> /dev/null; then
        actual=$(shasum -a 256 "$file" | cut -d' ' -f1)
    else
        warn "No SHA256 tool found. Skipping checksum verification."
        return 0
    fi

    if [ "$actual" != "$expected" ]; then
        error "Checksum verification failed!
  Expected: $expected
  Actual:   $actual
This could indicate a corrupted download or a security issue."
    fi

    info "Checksum verified"
}

# Download file using curl or wget (whichever is available)
# Best practice: Support multiple tools for broader compatibility
download() {
    local url="$1"
    local output="$2"

    if command -v curl &> /dev/null; then
        # -f: Fail on HTTP errors | -sS: Silent but show errors | -L: Follow redirects
        curl -fsSL "$url" -o "$output"
    elif command -v wget &> /dev/null; then
        wget -q "$url" -O "$output"
    else
        error "Neither curl nor wget found. Please install one of them."
    fi
}

# Main installation logic
main() {
    echo ""
    info "Installing $BINARY_NAME CLI..."
    echo ""

    # Step 1: Detect platform
    local os arch
    os=$(detect_os)
    arch=$(detect_arch)
    info "Platform: $os ($arch)"

    # Step 2: Determine version (user-specified or latest)
    local version
    version="${TTS_VERSION:-$(get_latest_version)}"
    info "Version: $version"

    # Step 3: Create isolated temp directory
    # Best practice: Use mktemp for secure temporary files
    TMP_DIR=$(mktemp -d)

    # Step 4: Build download URLs
    local binary_name download_url checksums_url
    binary_name=$(get_binary_name "$os" "$arch")
    download_url="$GITHUB_URL/releases/download/$version/$binary_name"
    checksums_url="$GITHUB_URL/releases/download/$version/checksums.txt"

    # Step 5: Download binary
    info "Downloading $binary_name..."
    download "$download_url" "$TMP_DIR/$binary_name"

    # Step 6: Verify checksum (security best practice)
    info "Verifying checksum..."
    if download "$checksums_url" "$TMP_DIR/checksums.txt" 2>/dev/null; then
        # Extract checksum for our binary from checksums file
        expected_checksum=$(grep "$binary_name" "$TMP_DIR/checksums.txt" | cut -d' ' -f1)
        if [ -n "$expected_checksum" ]; then
            verify_checksum "$TMP_DIR/$binary_name" "$expected_checksum"
        else
            warn "Checksum not found for $binary_name. Skipping verification."
        fi
    else
        warn "Checksums file not available. Skipping verification."
    fi

    # Step 7: Make binary executable
    chmod +x "$TMP_DIR/$binary_name"

    # Step 8: Ensure install directory exists
    if [ ! -d "$INSTALL_DIR" ]; then
        info "Creating $INSTALL_DIR..."
        # Check if we can write to parent directory
        if [ -w "$(dirname "$INSTALL_DIR")" ]; then
            mkdir -p "$INSTALL_DIR"
        else
            sudo mkdir -p "$INSTALL_DIR"
        fi
    fi

    # Step 9: Install binary (use sudo only if needed)
    # Best practice: Request minimal privileges
    info "Installing to $INSTALL_DIR/$BINARY_NAME..."
    if [ -w "$INSTALL_DIR" ]; then
        mv "$TMP_DIR/$binary_name" "$INSTALL_DIR/$BINARY_NAME"
    else
        sudo mv "$TMP_DIR/$binary_name" "$INSTALL_DIR/$BINARY_NAME"
    fi

    # Step 10: Verify installation and show next steps
    echo ""
    if command -v "$BINARY_NAME" &> /dev/null; then
        info "Successfully installed $BINARY_NAME $version"
        echo ""
        info "Get started:"
        echo "  $BINARY_NAME configure api-key    # Set your Fish Audio API key"
        echo "  $BINARY_NAME configure voice <id> # Set default voice model"
        echo "  $BINARY_NAME generate ./texts     # Generate speech from text files"
        echo ""
        info "Documentation: $GITHUB_URL"
    else
        # Binary installed but not in PATH
        warn "Installed to $INSTALL_DIR/$BINARY_NAME"
        warn "Add $INSTALL_DIR to your PATH or restart your terminal."
    fi
}

main "$@"
