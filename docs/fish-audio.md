# Fish Audio Reference

Quick reference for Fish Audio SDK and API.

## TTS (Text-to-Speech)

- [TTS SDK Guide](https://docs.fish.audio/sdk/tts) — `client.tts.convert()` usage
- [Audio Formats](https://docs.fish.audio/api-reference/tts#audio-formats) — mp3, wav, pcm output options
- [Emotions & Prosody](https://docs.fish.audio/features/ssml) — SSML-style control for expressiveness
- [Speed Control](https://docs.fish.audio/api-reference/tts#parameters) — 0.5x to 2.0x speech rate

### Supported Languages

Fish Audio supports **13 languages** with automatic detection:

```
English, Chinese, Japanese, German, French, Spanish, Korean,
Arabic, Russian, Dutch, Italian, Polish, Portuguese
```

Language detection is automatic - simply provide text in your target language.

## Voice Cloning

- [Voice Cloning SDK Guide](https://docs.fish.audio/sdk/voices) — `client.voices.create()` usage
- [Model Management](https://docs.fish.audio/api-reference/voices) — list, get, update, delete models
- [Audio Requirements](https://docs.fish.audio/features/voice-cloning) — sample quality, formats, transcripts

## API

- [API Reference](https://docs.fish.audio/api-reference) — full endpoint documentation
- [Authentication](https://docs.fish.audio/api-reference/authentication) — API key via `FISH_API_KEY`
- [Rate Limits](https://docs.fish.audio/api-reference/rate-limits) — request quotas and throttling
- [Error Handling](https://docs.fish.audio/api-reference/errors) — status codes and error responses
- [Python SDK (fishaudio)](https://pypi.org/project/fishaudio/) — pip install fishaudio
