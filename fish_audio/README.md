# Fish Audio

Scripts for managing voice models on Fish Audio.

## Scripts

- `scripts/upload_samples.py` — Upload audio samples to create a voice model

## Usage

```bash
export FISH_AUDIO_API_KEY=your_key

# Upload samples from a directory
python fish_audio/scripts/upload_samples.py ./samples --title "My Voice"

# With transcripts (place .txt files alongside audio files)
python fish_audio/scripts/upload_samples.py ./samples --title "My Voice" --enhance
```
