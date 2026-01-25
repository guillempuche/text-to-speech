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
tts update
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

## Supported Languages

Fish Audio auto-detects from 13 languages: English, Chinese, Japanese, German, French, Spanish, Korean, Arabic, Russian, Dutch, Italian, Polish, Portuguese.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and release process.
