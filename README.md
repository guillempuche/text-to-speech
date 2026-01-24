# Voice Cloning

Tools for creating persistent voice models on Fish Audio S1. Record audio samples, pair them with transcripts, and upload to Fish Audio to produce reusable voice models for text-to-speech.

## Getting Started

1. Install Nix via [Determinate Nix](https://docs.determinate.systems/determinate-nix) (if not already installed)
2. Enter the dev shell and set up your API key:

```bash
nix develop
cp .env.example .env
# Edit .env with your Fish Audio API key
```

## Usage

```bash
nix develop
python fish_audio/scripts/upload_samples.py ./samples --title "My Voice" --enhance
```

The `.env` file is auto-loaded. The script pairs each audio file with its matching `.txt` transcript by stem name (e.g. `en_1.wav` + `en_1.txt`).

Options: `--visibility private|public|unlist`, `--tags english male`, `--env-file /path`.

Prints the model ID on success for use with the Fish Audio TTS API.

## Development

```bash
lint      # Check formatting (no changes)
format    # Auto-fix formatting
```

Pre-commit hooks (lefthook) auto-format staged files on commit.

## Structure

- `fish_audio/` — Fish Audio integration (upload samples, manage models)
- `samples/` — Audio samples (gitignored) and transcripts (tracked)
