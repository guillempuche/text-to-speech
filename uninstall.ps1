#Requires -Version 5.1
<#
.SYNOPSIS
    Text-to-Speech CLI Uninstaller for Windows

.DESCRIPTION
    Removes the tts CLI tool, configuration files, and PATH entries.
    https://github.com/guillempuche/text-to-speech

.EXAMPLE
    irm https://raw.githubusercontent.com/guillempuche/text-to-speech/main/uninstall.ps1 | iex

.EXAMPLE
    # Keep configuration files
    $env:TTS_KEEP_CONFIG = "true"; irm ... | iex

.EXAMPLE
    # Custom install directory
    $env:TTS_INSTALL_DIR = "$HOME\bin"; irm ... | iex
#>

# Stop on any error
$ErrorActionPreference = "Stop"

# Configuration constants
$BinaryName = "tts"
$DefaultInstallDir = "$env:LOCALAPPDATA\Programs\tts"
$ConfigDir = "$HOME\.config\tts"
$KeyringService = "tts-cli"

# Allow user override via environment variable
$InstallDir = if ($env:TTS_INSTALL_DIR) { $env:TTS_INSTALL_DIR } else { $DefaultInstallDir }
$KeepConfig = if ($env:TTS_KEEP_CONFIG -eq "true") { $true } else { $false }

# Logging functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Green }
function Write-Warn { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Err { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red; exit 1 }

# Remove binary file
function Remove-Binary {
    $binaryPath = Join-Path $InstallDir "$BinaryName.exe"

    if (Test-Path $binaryPath) {
        Write-Info "Removing binary: $binaryPath"
        Remove-Item -Path $binaryPath -Force
        Write-Info "Binary removed"
    } else {
        Write-Warn "Binary not found at $binaryPath"
    }

    # Remove install directory if empty
    if ((Test-Path $InstallDir) -and ((Get-ChildItem $InstallDir | Measure-Object).Count -eq 0)) {
        Write-Info "Removing empty install directory: $InstallDir"
        Remove-Item -Path $InstallDir -Force
    }
}

# Remove from PATH environment variable
function Remove-FromPath {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

    if ($currentPath -like "*$InstallDir*") {
        Write-Info "Removing $InstallDir from PATH"

        # Remove the directory from PATH
        $pathParts = $currentPath -split ';' | Where-Object { $_ -ne $InstallDir -and $_ -ne "" }
        $newPath = $pathParts -join ';'

        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")

        # Also update current session
        $env:Path = ($env:Path -split ';' | Where-Object { $_ -ne $InstallDir }) -join ';'

        Write-Info "PATH updated"
        return $true
    }

    return $false
}

# Remove configuration directory
function Remove-Config {
    if ($KeepConfig) {
        Write-Info "Keeping configuration files (TTS_KEEP_CONFIG=true)"
        return
    }

    if (Test-Path $ConfigDir) {
        Write-Info "Removing configuration directory: $ConfigDir"
        Remove-Item -Path $ConfigDir -Recurse -Force
        Write-Info "Configuration removed"
    } else {
        Write-Info "No configuration directory found"
    }
}

# Remove Windows Credential Manager entry
function Remove-Credential {
    if ($KeepConfig) {
        return
    }

    Write-Info "Attempting to remove credential entry..."

    # Python keyring library stores credentials with target format that may vary
    # Try multiple possible formats used by keyring backends
    $targets = @(
        $KeyringService,
        "$KeyringService/api-key",
        "LegacyGeneric:target=$KeyringService"
    )

    $removed = $false
    foreach ($target in $targets) {
        try {
            $null = cmdkey /delete:$target 2>&1
            if ($LASTEXITCODE -eq 0) {
                $removed = $true
            }
        } catch {
            # Ignore errors, continue trying other formats
        }
    }

    if ($removed) {
        Write-Info "Credential Manager entry removed"
    } else {
        Write-Info "No Credential Manager entry found (or already removed)"
    }
}

# Main uninstallation logic
function Main {
    Write-Host ""
    Write-Info "Uninstalling $BinaryName CLI..."
    Write-Host ""

    Write-Info "Platform: windows"

    # Step 1: Remove binary
    Remove-Binary

    # Step 2: Remove from PATH
    $pathRemoved = Remove-FromPath

    # Step 3: Remove credential
    Remove-Credential

    # Step 4: Remove configuration files
    Remove-Config

    # Done
    Write-Host ""
    Write-Info "Uninstallation complete"

    if (-not $KeepConfig) {
        Write-Info "All $BinaryName files have been removed"
    } else {
        Write-Info "Binary removed. Configuration kept at $ConfigDir"
    }

    if ($pathRemoved) {
        Write-Host ""
        Write-Warn "Restart your terminal for PATH changes to take effect."
    }

    Write-Host ""
    Write-Info "To reinstall, run:"
    Write-Host "  irm https://raw.githubusercontent.com/guillempuche/text-to-speech/main/install.ps1 | iex"
}

Main
