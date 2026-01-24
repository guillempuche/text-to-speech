# AGENTS.md

Rules for humans and AI agents working in this repo.

## Golden Rules

1. **No secrets in git** — Use `.env.example` for variables
1. **Single source of truth** — Don't duplicate, reference instead
1. **Never commit audio samples to git** — Audio files are gitignored
1. **Keep transcripts alongside scripts** — Companion `.txt` files for audio

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

| Tool | Formats | Lint flag | Format flag |
|------|---------|-----------|-------------|
| dprint | Markdown, JSON, TOML | `dprint check` | `dprint fmt` |
| ruff | Python | `ruff check .` | `ruff check --fix . && ruff format .` |

Pre-commit hooks (lefthook) auto-format staged files on commit.
