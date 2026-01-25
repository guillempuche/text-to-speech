"""Tests for configure command."""

import pytest
from pathlib import Path

from tts.commands.configure import configure


class TestConfigure:
    """Tests for configure command."""

    def test_saves_api_key(self, temp_config_dir, capsys):
        """Configure should save API key to credentials file."""
        # GIVEN the config directory exists
        # WHEN configure is called with an API key
        configure("my-test-api-key")

        # THEN credentials file should be created
        creds_file = temp_config_dir / "credentials"
        assert creds_file.exists()
        # AND it should contain the key
        assert "FISH_API_KEY=my-test-api-key" in creds_file.read_text()

    def test_strips_whitespace_from_key(self, temp_config_dir):
        """Configure should strip whitespace from API key."""
        # GIVEN an API key with whitespace
        # WHEN configure is called
        configure("  spaced-key  ")

        # THEN the saved key should be trimmed
        creds_file = temp_config_dir / "credentials"
        assert "FISH_API_KEY=spaced-key" in creds_file.read_text()

    def test_sets_secure_permissions(self, temp_config_dir):
        """Credentials file should have restricted permissions."""
        # GIVEN configure is called
        configure("secret-key")

        # THEN file should be owner-only readable (0o600)
        creds_file = temp_config_dir / "credentials"
        assert (creds_file.stat().st_mode & 0o777) == 0o600

    def test_creates_config_directory(self, tmp_path, monkeypatch):
        """Configure should create config directory if missing."""
        # GIVEN config directory doesn't exist
        config_dir = tmp_path / "new_config" / "tts"
        monkeypatch.setattr("tts.commands.configure.CONFIG_DIR", config_dir)
        monkeypatch.setattr("tts.commands.configure.CREDENTIALS_FILE", config_dir / "credentials")

        # WHEN configure is called
        configure("new-key")

        # THEN directory should be created
        assert config_dir.exists()
        assert (config_dir / "credentials").exists()

    def test_rejects_empty_key(self, temp_config_dir, capsys):
        """Configure should reject empty API key."""
        # GIVEN an empty API key
        # WHEN configure is called
        # THEN it should exit with error
        with pytest.raises(SystemExit) as exc_info:
            configure("")

        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "empty" in output.lower()

    def test_rejects_whitespace_only_key(self, temp_config_dir, capsys):
        """Configure should reject whitespace-only API key."""
        # GIVEN a whitespace-only API key
        # WHEN configure is called
        # THEN it should exit with error
        with pytest.raises(SystemExit) as exc_info:
            configure("   ")

        assert exc_info.value.code == 1

    def test_overwrites_existing_credentials(self, temp_config_dir):
        """Configure should overwrite existing credentials file."""
        # GIVEN an existing credentials file
        creds_file = temp_config_dir / "credentials"
        creds_file.write_text("FISH_API_KEY=old-key\n")

        # WHEN configure is called with new key
        configure("new-key")

        # THEN file should contain new key only
        content = creds_file.read_text()
        assert "old-key" not in content
        assert "FISH_API_KEY=new-key" in content

    def test_prints_success_message(self, temp_config_dir, capsys):
        """Configure should print success message."""
        # GIVEN configure is called
        configure("test-key")

        # THEN success message should be printed
        output = capsys.readouterr().out
        assert "saved" in output.lower()
