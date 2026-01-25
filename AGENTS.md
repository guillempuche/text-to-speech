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

## CLI Structure

```
src/tts/
├── __init__.py          # Version
├── __main__.py          # python -m tts entry
├── cli.py               # Main app with subcommands
├── common.py            # Shared utilities (API key loading)
└── commands/
    ├── configure.py     # tts configure
    ├── generate.py      # tts generate
    ├── update.py        # tts update
    └── voice.py         # tts voice upload/list-models
```

Adding a new command:
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

## Docs

- `README.md` — User-facing install and usage
- `CONTRIBUTING.md` — Development setup and releases
- `CHANGELOG.md` — Release notes (source of truth)
- `docs/fish-audio.md` — SDK and API reference
