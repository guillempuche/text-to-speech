# Contributing

Development setup and release process for the TTS CLI.

## Setup

1. Install [Determinate Nix](https://docs.determinate.systems/determinate-nix)
2. Enter dev shell: `nix develop`
3. Configure: `tts configure <your-api-key>`

## Development

```bash
nix develop              # Enter shell
tts --help               # Test CLI
uv run tts generate ...  # Run with dependencies
uv run pytest            # Run tests
lint                     # Check formatting
format                   # Auto-fix formatting
```

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

### Adding a Command

1. Create `src/tts/commands/mycommand.py`
2. Import and register in `src/tts/cli.py`

## Releases

Uses calver versioning: `YYYY.MM.DD`

### Via AI

Run `/release` skill.

### Manual

1. Update `CHANGELOG.md` — Move [Unreleased] content to new version section
2. Update version in `pyproject.toml` and `src/tts/__init__.py`
3. Commit: `git commit -m "release: vYYYY.MM.DD"`
4. Tag and push: `git tag vYYYY.MM.DD && git push origin main vYYYY.MM.DD`

GitHub Actions builds executables for Linux, macOS (x64/arm64), and Windows.
