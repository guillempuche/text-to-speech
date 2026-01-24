# Text-to-Speech

Fish Audio tools — voice model creation and text-to-speech generation.

## Getting Started

1. Install Nix via [Determinate Nix](https://docs.determinate.systems/determinate-nix) (if not already installed)
2. Enter the dev shell and set up your API key:

```bash
nix develop
cp .env.example .env
# Edit .env with your Fish Audio API key
```

## Usage

### Voice Cloning

```bash
nix develop
python voice_cloning/scripts/upload_samples.py ./samples --title "My Voice" --enhance
```

Pairs each audio file with its matching `.txt` transcript by stem name (e.g. `en_1.wav` + `en_1.txt`). Prints the model ID on success.

Options: `--visibility private|public|unlist`, `--tags english male`, `--env-file /path`.

### TTS (Text-to-Speech)

```bash
nix develop
python tts/scripts/generate.py ./texts --reference-id <voice-model-id>
```

Converts `.txt` files to speech audio using a voice model. Each file produces an audio file with the same stem name.

Options: `--format mp3|wav|pcm`, `--speed 0.5-2.0`, `--output-dir ./path`, `--env-file /path`.

## Development

```bash
lint      # Check formatting (no changes)
format    # Auto-fix formatting
```

Pre-commit hooks (lefthook) auto-format staged files on commit.

## Structure

- `voice_cloning/` — Voice model creation (upload samples, manage models)
- `tts/` — Text-to-speech generation (convert text to audio)
- `docs/` — Fish Audio SDK and API reference
- `samples/` — Audio samples (gitignored) and transcripts (tracked)
