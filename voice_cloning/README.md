# Voice Cloning

Scripts for creating voice models on Fish Audio.

## Scripts

- `scripts/upload_samples.py` — Upload audio samples to create a voice model

## Usage

```bash
export FISH_API_KEY=your_key

# Upload samples (place audio + optional .txt transcripts in samples/)
python voice_cloning/scripts/upload_samples.py ./samples --title "My Voice"

# With enhancement and tags
python voice_cloning/scripts/upload_samples.py ./samples --title "My Voice" \
  --enhance --visibility private --tags english male
```

## Transcript convention

Place a `.txt` file with the same name as the audio file for each sample:

```
samples/
  sample1.wav
  sample1.txt    <- exact transcription of sample1.wav
  sample2.wav
  sample2.txt
```

Transcripts must be provided for ALL samples or none (partial is not supported).
Providing transcripts skips ASR and yields better quality.
