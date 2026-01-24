# TTS

Generate speech audio from text files using Fish Audio.

## Scripts

- `scripts/generate.py` — Convert text files to speech audio

## Usage

```bash
export FISH_API_KEY=your_key

# Generate from a directory of .txt files
python tts/scripts/generate.py ./texts --reference-id <voice-model-id>

# Single file, custom format and speed
python tts/scripts/generate.py ./input.txt --reference-id <id> \
  --format wav --speed 1.2 --output-dir ./output
```

The `.env` file is auto-loaded. Each `.txt` file produces an audio file with the same stem name.

Options: `--format mp3|wav|pcm`, `--speed 0.5-2.0`, `--output-dir ./path`, `--env-file /path`.
