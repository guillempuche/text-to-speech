#Requires -Version 5.1
<#
.SYNOPSIS
    Text-to-Speech CLI Installer for Windows

.DESCRIPTION
    Downloads and installs the tts CLI tool with checksum verification.
    https://github.com/guillempuche/text-to-speech

.EXAMPLE
    irm https://raw.githubusercontent.com/guillempuche/text-to-speech/main/install.ps1 | iex

.EXAMPLE
    # Install specific version
    $env:TTS_VERSION = "v2024.01.01"; irm ... | iex

.EXAMPLE
    # Custom install directory
    $env:TTS_INSTALL_DIR = "$HOME\bin"; irm ... | iex
#>

# Stop on any error - equivalent to bash's "set -e"
# Best practice: Fail fast to avoid partial installations
$ErrorActionPreference = "Stop"

# Configuration constants
$Repo = "guillempuche/text-to-speech"
$GithubUrl = "https://github.com/$Repo"
$BinaryName = "tts"

# Default install location: %LOCALAPPDATA%\Programs\tts
# Best practice: Use per-user directory to avoid requiring admin rights
$DefaultInstallDir = "$env:LOCALAPPDATA\Programs\tts"

# Allow user override via environment variable
# Best practice: Make scripts configurable without modification
$InstallDir = if ($env:TTS_INSTALL_DIR) { $env:TTS_INSTALL_DIR } else { $DefaultInstallDir }

# Logging functions with colored output and consistent prefixes
# Best practice: Use colors to distinguish message types
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Warn { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Err { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red; exit 1 }

# Fetch latest version tag from GitHub API
# Best practice: Use API instead of scraping HTML pages
function Get-LatestVersion {
    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -UseBasicParsing
        return $response.tag_name
    } catch {
        Write-Err "Failed to fetch latest version: $_"
    }
}

# Calculate SHA256 hash of a file
# Best practice: Use built-in cmdlets for security operations
function Get-FileHash256 {
    param($FilePath)
    $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
    return $hash.Hash.ToLower()  # Normalize to lowercase for comparison
}

# Verify downloaded file against expected checksum
# Best practice: Always verify downloads to detect corruption or tampering
function Test-Checksum {
    param($FilePath, $Expected)

    $actual = Get-FileHash256 -FilePath $FilePath

    if ($actual -ne $Expected.ToLower()) {
        Write-Err "Checksum verification failed!`n  Expected: $Expected`n  Actual:   $actual`nThis could indicate a corrupted download or a security issue."
    }

    Write-Info "Checksum verified"
}

# Add directory to user's PATH environment variable
# Best practice: Modify user PATH, not system PATH (no admin required)
function Add-ToPath {
    param($Directory)

    # Get current user PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

    # Check if directory already in PATH
    if ($currentPath -notlike "*$Directory*") {
        # Append to PATH and save to registry
        $newPath = "$currentPath;$Directory"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")

        # Also update current session
        $env:Path = "$env:Path;$Directory"

        Write-Info "Added $Directory to PATH"
        return $true
    }

    return $false
}

# Main installation logic
function Main {
    Write-Host ""
    Write-Info "Installing $BinaryName CLI..."
    Write-Host ""

    # Step 1: Check architecture (only 64-bit supported)
    $arch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
    if ($arch -ne "x64") {
        Write-Err "Only 64-bit Windows is supported"
    }
    Write-Info "Platform: windows ($arch)"

    # Step 2: Determine version (user-specified or latest)
    $version = if ($env:TTS_VERSION) { $env:TTS_VERSION } else { Get-LatestVersion }
    Write-Info "Version: $version"

    # Step 3: Create isolated temp directory using GUID for uniqueness
    # Best practice: Use unique temp directories to avoid conflicts
    $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

    try {
        # Step 4: Build download URLs
        $binaryName = "tts-windows-x64.exe"
        $downloadUrl = "$GithubUrl/releases/download/$version/$binaryName"
        $checksumsUrl = "$GithubUrl/releases/download/$version/checksums.txt"
        $tempFile = Join-Path $tempDir $binaryName

        # Step 5: Download binary
        # -UseBasicParsing: Works without IE engine (more compatible)
        Write-Info "Downloading $binaryName..."
        Invoke-WebRequest -Uri $downloadUrl -OutFile $tempFile -UseBasicParsing

        # Step 6: Verify checksum (security best practice)
        Write-Info "Verifying checksum..."
        try {
            $checksumsFile = Join-Path $tempDir "checksums.txt"
            Invoke-WebRequest -Uri $checksumsUrl -OutFile $checksumsFile -UseBasicParsing

            # Parse checksums file and find our binary
            $checksums = Get-Content $checksumsFile
            $line = $checksums | Where-Object { $_ -match $binaryName }

            if ($line) {
                # Extract hash (first field, space-separated)
                $expectedChecksum = ($line -split '\s+')[0]
                Test-Checksum -FilePath $tempFile -Expected $expectedChecksum
            } else {
                Write-Warn "Checksum not found for $binaryName. Skipping verification."
            }
        } catch {
            Write-Warn "Checksums file not available. Skipping verification."
        }

        # Step 7: Create install directory if needed
        if (-not (Test-Path $InstallDir)) {
            Write-Info "Creating $InstallDir..."
            New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        }

        # Step 8: Install binary
        $targetPath = Join-Path $InstallDir "$BinaryName.exe"
        Write-Info "Installing to $targetPath..."
        Move-Item -Path $tempFile -Destination $targetPath -Force

        # Step 9: Add to PATH if not already present
        $pathAdded = Add-ToPath -Directory $InstallDir

        # Step 10: Show success message and next steps
        Write-Host ""
        Write-Info "Successfully installed $BinaryName $version"
        Write-Host ""
        Write-Info "Get started:"
        Write-Host "  $BinaryName configure api-key    # Set your Fish Audio API key"
        Write-Host "  $BinaryName configure voice <id> # Set default voice model"
        Write-Host "  $BinaryName generate .\texts     # Generate speech from text files"
        Write-Host ""
        Write-Info "Documentation: $GithubUrl"

        # Remind user to restart terminal if PATH was modified
        if ($pathAdded) {
            Write-Host ""
            Write-Warn "Restart your terminal for PATH changes to take effect."
        }

    } finally {
        # Cleanup temp directory - runs even if errors occur
        # Best practice: Always clean up temporary files
        if (Test-Path $tempDir) {
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

Main
