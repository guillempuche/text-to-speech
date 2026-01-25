# Text-to-Speech

Fish Audio CLI for voice cloning and text-to-speech generation.

## Install

### macOS (Apple Silicon)

```bash
curl -L -o tts https://github.com/guillempuche/text-to-speech/releases/latest/download/tts-macos-arm64
chmod +x tts
sudo mv tts /usr/local/bin/  # Optional: add to PATH
```

### macOS (Intel)

```bash
curl -L -o tts https://github.com/guillempuche/text-to-speech/releases/latest/download/tts-macos-x64
chmod +x tts
```

### Linux

```bash
curl -L -o tts https://github.com/guillempuche/text-to-speech/releases/latest/download/tts-linux-x64
chmod +x tts
```

### Windows

Download `tts-windows-x64.exe` from [Releases](https://github.com/guillempuche/text-to-speech/releases/latest).

## Quick Start

```bash
# Configure your API key (get one at https://fish.audio)
tts configure <your-api-key>

# Generate speech from text files
tts generate ./texts --reference-id <voice-model-id>

# Upload voice samples to create a model
tts voice upload ./samples --title "My Voice"
```

## Update

```bash
# Check for updates
tts update

# Update manually
curl -L -o tts https://github.com/guillempuche/text-to-speech/releases/latest/download/tts-macos-arm64
chmod +x tts
```

## Commands

```
tts configure <api-key>     Save API key for future use
tts generate                Convert text files to speech
tts voice upload            Upload samples to create voice model
tts voice list-models       List your voice models
tts update                  Check for updates
```

### Generate Speech

```bash
tts generate ./texts --reference-id <voice-model-id>
```

Options:
- `--format mp3|wav|pcm` (default: mp3)
- `--speed 0.5-2.0` (default: 1.0)
- `--output-dir ./path` (default: ./audio_output)

### Voice Cloning

```bash
tts voice upload ./samples --title "My Voice" --enhance
```

Pairs each audio file with its matching `.txt` transcript (e.g. `en_1.wav` + `en_1.txt`).

Options:
- `--visibility private|public|unlist`
- `--tags english male`
- `--enhance` (audio quality enhancement)

## Development

1. Install [Determinate Nix](https://docs.determinate.systems/determinate-nix)
2. Enter dev shell: `nix develop`
3. Configure: `tts configure <your-api-key>`

```bash
uv run pytest   # Run tests
lint            # Check formatting
format          # Auto-fix formatting
```

## Releases

Push a calver tag to trigger a release build:

```bash
git tag v2025.01.25
git push origin v2025.01.25
```

Builds for Linux, macOS (x64/arm64), and Windows.
