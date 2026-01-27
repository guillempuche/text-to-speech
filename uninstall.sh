#!/bin/bash
#
# Text-to-Speech CLI Uninstaller
# https://github.com/guillempuche/text-to-speech
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/guillempuche/text-to-speech/main/uninstall.sh | bash
#
# Environment variables:
#   TTS_INSTALL_DIR - Installation directory (default: /usr/local/bin)
#   TTS_KEEP_CONFIG - Set to "true" to keep configuration files
#

# -e: Exit on error | -u: Error on undefined vars | -o pipefail: Catch pipe failures
set -euo pipefail

# Configuration constants
BINARY_NAME="tts"
DEFAULT_INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.config/tts"
KEYRING_SERVICE="tts-cli"

# Allow user override via environment variable
INSTALL_DIR="${TTS_INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"
KEEP_CONFIG="${TTS_KEEP_CONFIG:-false}"

# Terminal colors - disabled when output is piped (not a TTY)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' NC=''
fi

# Logging functions
info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; exit 1; }

# Detect operating system
detect_os() {
    local os
    os="$(uname -s)"
    case "$os" in
        Linux*)  echo "linux" ;;
        Darwin*) echo "macos" ;;
        MINGW*|MSYS*|CYGWIN*)
            error "Windows detected. Please use the PowerShell uninstaller instead:
  irm https://raw.githubusercontent.com/guillempuche/text-to-speech/main/uninstall.ps1 | iex"
            ;;
        *) error "Unsupported operating system: $os" ;;
    esac
}

# Remove binary file
remove_binary() {
    local binary_path="$INSTALL_DIR/$BINARY_NAME"

    if [ -f "$binary_path" ]; then
        info "Removing binary: $binary_path"
        if [ -w "$INSTALL_DIR" ]; then
            rm -f "$binary_path"
        else
            sudo rm -f "$binary_path"
        fi
        info "Binary removed"
    else
        warn "Binary not found at $binary_path"
    fi
}

# Remove configuration directory
remove_config() {
    if [ "$KEEP_CONFIG" = "true" ]; then
        info "Keeping configuration files (TTS_KEEP_CONFIG=true)"
        return
    fi

    if [ -d "$CONFIG_DIR" ]; then
        info "Removing configuration directory: $CONFIG_DIR"
        rm -rf "$CONFIG_DIR"
        info "Configuration removed"
    else
        info "No configuration directory found"
    fi
}

# Remove keyring entry (best effort - may require user interaction)
remove_keyring() {
    local os="$1"

    if [ "$KEEP_CONFIG" = "true" ]; then
        return
    fi

    info "Attempting to remove keyring entry..."

    case "$os" in
        macos)
            # macOS Keychain - delete generic password
            # Requires both service (-s) and account (-a) to match keyring library format
            if security delete-generic-password -s "$KEYRING_SERVICE" -a "api-key" 2>/dev/null; then
                info "Keychain entry removed"
            else
                info "No keychain entry found (or already removed)"
            fi
            ;;
        linux)
            # Linux Secret Service - try using secret-tool if available
            if command -v secret-tool &> /dev/null; then
                # Must match both service and username attributes from keyring library
                if secret-tool clear service "$KEYRING_SERVICE" username "api-key" 2>/dev/null; then
                    info "Secret Service entry removed"
                else
                    info "No Secret Service entry found (or already removed)"
                fi
            else
                info "secret-tool not found - skipping keyring cleanup"
                info "You may need to manually remove the '$KEYRING_SERVICE' entry from your keyring"
            fi
            ;;
    esac
}

# Main uninstallation logic
main() {
    echo ""
    info "Uninstalling $BINARY_NAME CLI..."
    echo ""

    # Detect platform
    local os
    os=$(detect_os)
    info "Platform: $os"

    # Step 1: Remove binary
    remove_binary

    # Step 2: Remove keyring entry
    remove_keyring "$os"

    # Step 3: Remove configuration files
    remove_config

    # Done
    echo ""
    info "Uninstallation complete"

    if [ "$KEEP_CONFIG" != "true" ]; then
        info "All $BINARY_NAME files have been removed"
    else
        info "Binary removed. Configuration kept at $CONFIG_DIR"
    fi

    echo ""
    info "To reinstall, run:"
    echo "  curl -fsSL https://raw.githubusercontent.com/guillempuche/text-to-speech/main/install.sh | bash"
}

main "$@"
