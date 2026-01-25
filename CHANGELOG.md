# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/)
Versioning: [CalVer](https://calver.org/) (YYYY.MM.DD)

## [Unreleased]

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

<!-- Release template:
## [YYYY.MM.DD]

### Added
- New features

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
-->
