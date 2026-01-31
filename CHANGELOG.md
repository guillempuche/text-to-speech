# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/)
Versioning: [CalVer](https://calver.org/) (YYYY.MM.DD)

## [Unreleased]

## [2026.01.31]

### Added

- `tts voice list` command as simpler alias for `tts voice list-models`
- Detailed voice output showing visibility, languages, tags, state, and creation date
- Uses `self_only=True` to list only user's own voices per official Fish Audio API

## [2026.01.27.1]

### Added

- Cross-platform uninstall scripts (`uninstall.sh`, `uninstall.ps1`)
- Uninstall documentation in README
- Reorganized AGENTS.md with key files reference

## [2026.01.27]

### Added

- Cross-platform install scripts (`install.sh`, `install.ps1`)
- SHA256 checksum verification for downloads
- Auto PATH configuration on Windows

## [2026.01.25.1]

### Added

- Config system with TOML storage (`~/.config/tts/config.toml`)
- Keyring storage for secure API key management
- Configure subcommands: `api-key`, `voice`, `output-dir`, `format`, `speed`
- `--show` and `--reset` flags for configure command
- Glob pattern support for generate: `*.txt`, `**/*.txt`
- Config defaults for generate options

## [2026.01.25]

### Added

- Unified CLI with subcommands (`tts generate`, `tts voice upload`, `tts configure`)
- `tts update` command to check for new versions
- GitHub Actions workflow for cross-platform builds (Linux, macOS, Windows)
- PyApp-based executable distribution
- API key storage in `~/.config/tts/credentials`

### Changed

- Restructured from separate scripts to `src/tts/` package
- Switched to calver versioning (YYYY.MM.DD)
