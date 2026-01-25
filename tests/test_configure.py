"""Tests for configure command."""

import pytest
from pathlib import Path

from tts.commands.configure import (
    configure_api_key,
    configure_voice,
    configure_output_dir,
    configure_format,
    configure_speed,
    _mask_key,
    _show_config,
    _reset_all,
)


class TestMaskKey:
    """Tests for _mask_key utility."""

    def test_masks_long_key(self):
        """Should mask middle of long keys."""
        # GIVEN a long key
        key = "abcd1234efgh5678"

        # WHEN masking
        result = _mask_key(key)

        # THEN first 4 and last 4 should be visible
        assert result == "abcd********5678"

    def test_masks_short_key(self):
        """Should fully mask short keys."""
        # GIVEN a short key
        key = "abc"

        # WHEN masking
        result = _mask_key(key)

        # THEN should be all asterisks
        assert result == "***"

    def test_masks_exactly_8_chars(self):
        """Should fully mask 8-char keys."""
        # GIVEN an 8-char key
        key = "12345678"

        # WHEN masking
        result = _mask_key(key)

        # THEN should be all asterisks
        assert result == "********"


class TestConfigureApiKey:
    """Tests for configure_api_key command."""

    def test_saves_api_key_to_credentials(
        self, temp_config_dir, mock_keyring_unavailable, capsys
    ):
        """Should save API key to credentials file when keyring unavailable."""
        # GIVEN keyring is unavailable
        # WHEN configure_api_key is called
        configure_api_key("my-test-api-key")

        # THEN credentials file should be created
        creds_file = temp_config_dir / "credentials"
        assert creds_file.exists()
        assert "FISH_API_KEY=my-test-api-key" in creds_file.read_text()

    def test_saves_api_key_to_keyring(
        self, temp_config_dir, mock_keyring_available, capsys
    ):
        """Should save API key to keyring when available."""
        # GIVEN keyring is available
        # WHEN configure_api_key is called
        configure_api_key("keyring-api-key")

        # THEN key should be in mock keyring storage
        assert mock_keyring_available.get("tts-cli:api-key") == "keyring-api-key"
        # AND success message should mention keyring
        output = capsys.readouterr().out
        assert "keyring" in output.lower()

    def test_strips_whitespace(self, temp_config_dir, mock_keyring_unavailable):
        """Should strip whitespace from API key."""
        # GIVEN a key with whitespace
        configure_api_key("  spaced-key  ")

        # THEN saved key should be trimmed
        creds_file = temp_config_dir / "credentials"
        assert "FISH_API_KEY=spaced-key" in creds_file.read_text()

    def test_sets_secure_permissions(self, temp_config_dir, mock_keyring_unavailable):
        """Credentials file should have restricted permissions."""
        # GIVEN configure is called
        configure_api_key("secret-key")

        # THEN file should be owner-only readable (0o600)
        creds_file = temp_config_dir / "credentials"
        assert (creds_file.stat().st_mode & 0o777) == 0o600

    def test_rejects_empty_key(self, temp_config_dir, capsys):
        """Should reject empty API key."""
        # GIVEN an empty API key
        # WHEN configure_api_key is called
        # THEN it should exit with error
        with pytest.raises(SystemExit) as exc_info:
            configure_api_key("")

        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "empty" in output.lower()

    def test_rejects_whitespace_only_key(self, temp_config_dir, capsys):
        """Should reject whitespace-only API key."""
        # GIVEN a whitespace-only key
        # WHEN configure_api_key is called
        with pytest.raises(SystemExit) as exc_info:
            configure_api_key("   ")

        assert exc_info.value.code == 1

    def test_prints_success_message(
        self, temp_config_dir, mock_keyring_unavailable, capsys
    ):
        """Should print success message."""
        # GIVEN configure is called
        configure_api_key("test-key")

        # THEN success message should be printed
        output = capsys.readouterr().out
        assert "saved" in output.lower()


class TestConfigureVoice:
    """Tests for configure_voice command."""

    def test_sets_default_voice(self, temp_config_dir, capsys):
        """Should set default voice in config."""
        # GIVEN no existing config
        # WHEN setting voice
        configure_voice("voice-123")

        # THEN config file should have voice
        from tts.config import load_config

        config = load_config()
        assert config.default_voice == "voice-123"

    def test_prints_confirmation(self, temp_config_dir, capsys):
        """Should print confirmation."""
        # GIVEN setting voice
        configure_voice("voice-456")

        # THEN confirmation should be printed
        output = capsys.readouterr().out
        assert "voice-456" in output

    def test_rejects_empty_voice(self, temp_config_dir, capsys):
        """Should reject empty voice ID."""
        # GIVEN empty voice
        # WHEN configuring
        with pytest.raises(SystemExit) as exc_info:
            configure_voice("")

        assert exc_info.value.code == 1


class TestConfigureOutputDir:
    """Tests for configure_output_dir command."""

    def test_sets_output_dir(self, temp_config_dir):
        """Should set default output directory."""
        # GIVEN no existing config
        # WHEN setting output dir
        configure_output_dir("/custom/path")

        # THEN config should be updated
        from tts.config import load_config

        config = load_config()
        assert config.output_dir == "/custom/path"

    def test_rejects_empty_path(self, temp_config_dir, capsys):
        """Should reject empty path."""
        with pytest.raises(SystemExit) as exc_info:
            configure_output_dir("")

        assert exc_info.value.code == 1


class TestConfigureFormat:
    """Tests for configure_format command."""

    def test_sets_format(self, temp_config_dir):
        """Should set default format."""
        # GIVEN no existing config
        # WHEN setting format
        configure_format("wav")

        # THEN config should be updated
        from tts.config import load_config

        config = load_config()
        assert config.format == "wav"


class TestConfigureSpeed:
    """Tests for configure_speed command."""

    def test_sets_speed(self, temp_config_dir):
        """Should set default speed."""
        # GIVEN no existing config
        # WHEN setting speed
        configure_speed(1.5)

        # THEN config should be updated
        from tts.config import load_config

        config = load_config()
        assert config.speed == 1.5

    def test_rejects_low_speed(self, temp_config_dir, capsys):
        """Should reject speed below 0.5."""
        with pytest.raises(SystemExit) as exc_info:
            configure_speed(0.4)

        assert exc_info.value.code == 1

    def test_rejects_high_speed(self, temp_config_dir, capsys):
        """Should reject speed above 2.0."""
        with pytest.raises(SystemExit) as exc_info:
            configure_speed(2.1)

        assert exc_info.value.code == 1


class TestShowConfig:
    """Tests for --show flag."""

    def test_shows_config(self, temp_config_dir, capsys, mock_keyring_unavailable):
        """Should display current configuration."""
        # GIVEN a config exists
        from tts.config import save_config, TTSConfig

        save_config(TTSConfig(default_voice="test-voice", format="wav"))

        # WHEN showing config
        _show_config()

        # THEN output should contain config values
        output = capsys.readouterr().out
        assert "test-voice" in output
        assert "wav" in output


class TestResetAll:
    """Tests for --reset flag."""

    def test_resets_config(self, temp_config_dir, mock_keyring_unavailable, capsys):
        """Should reset all configuration."""
        # GIVEN custom config and credentials
        from tts.config import save_config, TTSConfig, load_config

        save_config(TTSConfig(format="wav"))
        creds_file = temp_config_dir / "credentials"
        creds_file.write_text("FISH_API_KEY=old-key\n")

        # WHEN resetting
        _reset_all()

        # THEN config should be defaults
        config = load_config()
        assert config.format == "mp3"
        # AND credentials should be removed
        assert not creds_file.exists()
