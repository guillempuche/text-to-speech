---
name: commits
description: Commits changes to the text-to-speech repo with clear, conventional messages. Use when committing, saving changes, or asked to commit.
---

# Commit

Commits with conventional format suited for this repo.

## Format

```
<type>(<scope>): <short description>
```

Scope is purely optional — only when truly required.

## Types

| Type      | When                                     |
| --------- | ---------------------------------------- |
| `voice`   | Voice samples config, model references   |
| `tts`     | Text-to-speech scripts, generation       |
| `scripts` | Python scripts for uploading, processing |
| `ai`      | Claude config, skills, hooks (.claude/)  |
| `chore`   | Config, cleanup, structure               |
| `docs`    | READMEs, documentation                   |
| `infra`   | Nix, CI, formatting config               |

## Scopes (purely optional)

Subfolder names. Only use when truly needed for clarity.

| Scope           | When                     |
| --------------- | ------------------------ |
| `voice_cloning` | Voice cloning scripts    |
| `tts`           | TTS generation scripts   |
| `samples`       | Audio samples management |

Both lists evolve — check actual structure.

## Rules

1. Lowercase, no period at end
1. Imperative mood ("add" not "added")
1. Body optional — only when context needed
1. Body format: bullet points, past tense, period at end
1. Never add AI attribution (no "Co-Authored-By", "Generated with", etc.)

## Examples

```
voice: add model reference for narrator
scripts: add upload samples script
ai: add commit skill
chore: restructure folders
docs: update README
infra: add dprint config
```

With body (when needed):

```
scripts(voice_cloning): update upload with transcript support

- Added companion .txt file reading.
- Added --enhance flag for audio enhancement.
- Updated error handling for missing API key.
```

## Workflow

1. `git status` — see what changed

1. `git diff` — review changes

1. **Propose commits:**

   - If conversation discussed a specific topic → propose single commit for that topic only
   - Otherwise → propose multiple commits, one per logical change

1. **Always preview** — for each proposed commit show:

   ```
   Commit 1:
     <message>
     git add <files>
   ```

   (repeat for each commit if multiple)

1. **Wait for user approval** — never commit without explicit approval

1. Execute approved commits

1. Don't push unless asked
