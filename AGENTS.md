# AGENTS.md

Rules for humans and AI agents working in this repo.

## What This Repo Does

Manages voice cloning through Fish Audio S1. Record audio samples, pair with text transcripts, upload to Fish Audio, get a persistent voice model ID for TTS.

Voice models support English and Spanish generation. Fish Audio separates language (from input text) from voice characteristics (from reference audio), so a Spanish-recorded sample produces Spanish-accented English when given English text.

See `README.md` for setup (including Nix installation) and usage.

## Golden Rules

1. **No secrets in git** — Use `.env.example` for variables
1. **Single source of truth** — Don't duplicate, reference instead
1. **Never commit audio samples to git** — `samples/` content is gitignored
1. **Keep transcripts alongside audio** — Companion `.txt` files with exact transcriptions

## Development

### Nix Shell

```bash
# Enter the dev shell (installs all tools)
nix develop

# Then run commands directly:
lint        # Check formatting (no changes)
format      # Format all files (auto-fix)
```

### Without Nix Shell

```bash
# One-off commands (no need to enter shell):
nix develop -c lint
nix develop -c format
```

### Tools

| Tool   | Formats              | Lint flag      | Format flag                           |
| ------ | -------------------- | -------------- | ------------------------------------- |
| dprint | Markdown, JSON, TOML | `dprint check` | `dprint fmt`                          |
| ruff   | Python               | `ruff check .` | `ruff check --fix . && ruff format .` |

Pre-commit hooks (lefthook) auto-format staged files on commit.
