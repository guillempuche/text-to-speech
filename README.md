# Text-to-Speech

Fish Audio CLI for voice cloning and text-to-speech generation.

```
┌────────────────────────────────────────────────┐
│                                                │
│  YOUR TEXT       tts generate        AUDIO    │
│  ┌────────┐      ───────────>      ┌───────┐  │
│  │ Hello, │                        │ ))) ) │  │
│  │ world! │    --reference-id      │ .mp3  │  │
│  └────────┘       <voice-id>       └───────┘  │
│    .txt                                       │
│                                               │
├───────────────────────┬───────────────────────┤
│                       │                       │
│  CLONE YOUR VOICE     │  BATCH PROCESS        │
│  ─────────────────    │  ─────────────        │
│  Upload samples +     │  tts generate "*.txt" │
│  transcripts to       │  tts generate "**/*"  │
│  create custom        │                       │
│  voice models         │  Glob patterns for    │
│                       │  multiple files       │
│                       │                       │
└───────────────────────┴───────────────────────┘
```

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
tts configure api-key

# Set a default voice model
tts configure voice <voice-model-id>

# Generate speech from text files
tts generate ./texts

# Or use glob patterns for batch processing
tts generate "**/*.txt"
```

## Update

```bash
tts update
```

## Commands

### Configure

```bash
tts configure              # Interactive configuration wizard
tts configure api-key      # Set API key (secure prompt)
tts configure voice <id>   # Set default voice model
tts configure output-dir <path>  # Set default output directory
tts configure format <fmt> # Set default format (mp3|wav|pcm)
tts configure speed <val>  # Set default speed (0.5-2.0)
tts configure --show       # Show current configuration
tts configure --reset      # Reset to defaults
```

### Generate Speech

```bash
tts generate <path-or-pattern> --reference-id <voice-model-id>
```

Supports multiple input formats:

```bash
tts generate ./file.txt              # Single file
tts generate ./texts                 # All .txt in directory
tts generate "*.txt"                 # Glob: current directory
tts generate "scripts/*.txt"         # Glob: specific directory
tts generate "**/*.txt"              # Glob: recursive search
```

Options:

| Option | Description | Default |
|--------|-------------|---------|
| `--reference-id` | Voice model ID | Config default |
| `--format` | Output format (mp3\|wav\|pcm) | mp3 |
| `--speed` | Speech speed (0.5-2.0) | 1.0 |
| `--output-dir` | Output directory | ./audio_output |
| `--env-file` | Path to .env file | - |

### Voice Cloning

```bash
tts voice upload ./samples --title "My Voice"
```

Pairs each audio file with its matching `.txt` transcript (e.g. `en_1.wav` + `en_1.txt`).

Options:

| Option | Description | Default |
|--------|-------------|---------|
| `--title` | Voice model name | Required |
| `--visibility` | private\|public\|unlist | private |
| `--tags` | Space-separated tags | - |
| `--enhance` | Audio quality enhancement | - |

### List Voice Models

```bash
tts voice list-models
```

## Configuration

### Config File

Settings are stored in `~/.config/tts/config.toml`:

```toml
default_voice = "your-voice-id"
output_dir = "./audio_output"
format = "mp3"
speed = 1.0
```

### API Key Storage

The API key is stored securely with the following priority:

1. **Environment variable**: `FISH_API_KEY`
2. **System keyring**: Secure OS credential storage (macOS Keychain, Windows Credential Manager, Linux Secret Service)
3. **Credentials file**: `~/.config/tts/credentials` (permissions: 600)
4. **Local .env file**: `.env` in current directory

When using `tts configure api-key`, the CLI automatically uses keyring if available, falling back to the credentials file.

## Supported Languages

Fish Audio auto-detects from 13 languages: English, Chinese, Japanese, German, French, Spanish, Korean, Arabic, Russian, Dutch, Italian, Polish, Portuguese.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and release process.
