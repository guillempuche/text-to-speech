---
name: release
description: Release and deploy a new version of the TTS CLI. Updates version files, commits, tags, and pushes to trigger GitHub Actions build. Use when releasing, deploying, publishing, or creating a new version.
allowed-tools: Bash(git:*) Bash(gh:*) Read Edit
---

# Release

Releases a new version using calver (YYYY.MM.DD) and triggers GitHub Actions to build executables.

## Versioning

This project uses **calver**: `YYYY.MM.DD`

- Format: `2025.01.25`
- Tag format: `v2025.01.25`
- If multiple releases same day: `2025.01.25.1`, `2025.01.25.2`

## Files to Update

1. `pyproject.toml` → `version = "YYYY.MM.DD"`
2. `src/tts/__init__.py` → `__version__ = "YYYY.MM.DD"`
3. `CHANGELOG.md` → Move [Unreleased] to new version section

## Workflow

### 1. Check Unreleased Changes

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

If no commits since last tag, abort release.

### 2. Generate Release Notes

Read `CHANGELOG.md` and check [Unreleased] section. If empty, generate from commits:

```bash
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"- %s"
```

Categorize commits by type prefix:
- `feat:`, `add:` → Added
- `fix:` → Fixed
- `change:`, `refactor:` → Changed
- `remove:`, `delete:` → Removed
- `docs:` → skip (or add to Changed)
- `chore:`, `infra:`, `ci:` → skip

### 3. Determine Version

```bash
date +%Y.%m.%d
git tag -l "v$(date +%Y.%m.%d)*"
```

### 4. Update CHANGELOG.md

Transform:

```markdown
## [Unreleased]

### Added
- New feature X
```

Into:

```markdown
## [Unreleased]

## [2025.01.25]

### Added
- New feature X
```

### 5. Update Version Files

- `pyproject.toml`: `version = "<new-version>"`
- `src/tts/__init__.py`: `__version__ = "<new-version>"`

### 6. Commit and Tag

```bash
git add pyproject.toml src/tts/__init__.py CHANGELOG.md
git commit -m "release: v<version>"
git tag v<version>
```

### 7. Push

```bash
git push origin main
git push origin v<version>
```

### 8. Report

```bash
gh run list --limit 3
```

Provide:
- Release notes summary
- Release URL: `https://github.com/guillempuche/text-to-speech/releases/tag/v<version>`
- Actions URL: `https://github.com/guillempuche/text-to-speech/actions`

## Example Session

```
User: release

AI: Checking for unreleased changes...

Commits since v2025.01.24:
- feat: add update command
- fix: handle empty API response
- docs: update README

Generating release notes...

## [2025.01.25]

### Added
- Update command to check for new versions

### Fixed
- Handle empty API response gracefully

Updating files:
- pyproject.toml: 2025.01.24 → 2025.01.25
- src/tts/__init__.py: 2025.01.24 → 2025.01.25
- CHANGELOG.md: moved Unreleased to 2025.01.25

Commit: release: v2025.01.25
Tag: v2025.01.25
Pushing...

Release triggered!
- Monitor: https://github.com/guillempuche/text-to-speech/actions
- Release: https://github.com/guillempuche/text-to-speech/releases/tag/v2025.01.25
```

## Pre-flight Checks

1. **Clean working tree** — no uncommitted changes
2. **On main branch** — releases from main only
3. **Unreleased changes exist** — don't release empty versions
4. **CHANGELOG has content** — or generate from commits

## Rollback

```bash
git push origin :refs/tags/v<version>
git tag -d v<version>
git revert HEAD
git push origin main
```
