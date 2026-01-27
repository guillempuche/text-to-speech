# AGENTS.md

Rules for humans and AI agents working in this repo.

## What This Repo Does

Fish Audio CLI for voice cloning and text-to-speech generation.

- **`tts generate`**: Convert text files to speech using voice models
- **`tts voice upload`**: Create voice models from audio samples + transcripts
- **`tts configure`**: Save API key for CLI usage
- **`tts update`**: Check for new versions

Fish Audio supports 13 languages with auto-detection (English, Chinese, Japanese, German, French, Spanish, Korean, Arabic, Russian, Dutch, Italian, Polish, Portuguese).

## Golden Rules

1. **No secrets in git** — Use `tts configure` or `.env`
1. **Single source of truth** — Don't duplicate, reference instead
1. **Never commit audio samples** — `samples/` content is gitignored
1. **Keep transcripts with audio** — Companion `.txt` files with exact transcriptions
1. **Calver versioning** — Format: `YYYY.MM.DD` (e.g., `2025.01.25`)
1. **CHANGELOG is source of truth** — GitHub release notes are extracted from it

## Key Files

### Installation & Distribution

| File | Purpose |
|------|---------|
| `install.sh` | Unix/macOS installer (curl \| bash) |
| `install.ps1` | Windows PowerShell installer |
| `uninstall.sh` | Unix/macOS uninstaller |
| `uninstall.ps1` | Windows PowerShell uninstaller |
| `pyproject.toml` | Python project config, version, dependencies |
| `.github/workflows/release.yml` | CI/CD: builds binaries, creates releases |

### CLI Source Code

```
src/tts/
├── __init__.py          # Version string
├── __main__.py          # python -m tts entry point
├── cli.py               # Main app, subcommand registration
├── config.py            # Config file management (~/.config/tts/config.toml)
├── common.py            # Shared utilities, API key loading, keyring
└── commands/
    ├── configure.py     # tts configure
    ├── generate.py      # tts generate
    ├── update.py        # tts update
    └── voice.py         # tts voice upload/list-models
```

### Configuration Locations (Runtime)

| Location | Content |
|----------|---------|
| `~/.config/tts/config.toml` | User settings (voice, format, speed) |
| `~/.config/tts/credentials` | API key fallback (if keyring unavailable) |
| System keyring | API key (macOS Keychain, Windows Credential Manager, Linux Secret Service) |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | User-facing install and usage |
| `CONTRIBUTING.md` | Development setup and workflow |
| `CHANGELOG.md` | Release notes (source of truth for releases) |
| `docs/fish-audio.md` | Fish Audio SDK and API reference |

### README Topics (for user-facing docs)

The README covers these sections in order:
- **Install** — `install.sh`, `install.ps1`, env vars (`TTS_VERSION`, `TTS_INSTALL_DIR`)
- **Quick Start** — API key setup, default voice, generate examples
- **Update** — `tts update` command
- **Uninstall** — `uninstall.sh`, `uninstall.ps1`, env vars (`TTS_KEEP_CONFIG`)
- **Commands** — Configure, Generate, Voice cloning, List models
- **Configuration** — Config file format, API key storage priority
- **Supported Languages** — 13 languages with auto-detection

## Adding a New Command

1. Create `src/tts/commands/mycommand.py`
2. Import and register in `src/tts/cli.py`

## Development

```bash
nix develop              # Enter shell
tts --help               # Test CLI
uv run tts generate ...  # Run with dependencies
uv run pytest            # Run tests
lint                     # Check formatting
format                   # Auto-fix
```

## Releasing

Use `/release` skill or manually:

1. **Update CHANGELOG.md** — Move [Unreleased] content to new version section
2. **Update version** in `pyproject.toml` and `src/tts/__init__.py`
3. **Commit**: `git commit -m "release: v2025.01.25"`
4. **Tag and push**: `git tag v2025.01.25 && git push origin main v2025.01.25`

GitHub Actions:
- Builds executables for Linux, macOS (x64/arm64), Windows
- Extracts release notes from CHANGELOG.md
- Creates GitHub Release with binaries
