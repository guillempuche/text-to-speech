"""Tests for config module."""

import pytest
from pathlib import Path

from tts.config import TTSConfig, load_config, save_config, update_config, reset_config


class TestTTSConfig:
    """Tests for TTSConfig dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        # GIVEN a new config
        config = TTSConfig()

        # THEN defaults should be set
        assert config.default_voice is None
        assert config.output_dir == "./audio_output"
        assert config.format == "mp3"
        assert config.speed == 1.0

    def test_validates_format(self):
        """Should reject invalid format values."""
        # GIVEN an invalid format
        # WHEN creating config
        # THEN it should raise ValueError
        with pytest.raises(ValueError, match="Invalid format"):
            TTSConfig(format="invalid")

    def test_validates_speed_too_low(self):
        """Should reject speed below 0.5."""
        # GIVEN speed below 0.5
        # WHEN creating config
        # THEN it should raise ValueError
        with pytest.raises(ValueError, match="Speed must be"):
            TTSConfig(speed=0.4)

    def test_validates_speed_too_high(self):
        """Should reject speed above 2.0."""
        # GIVEN speed above 2.0
        # WHEN creating config
        # THEN it should raise ValueError
        with pytest.raises(ValueError, match="Speed must be"):
            TTSConfig(speed=2.1)

    def test_accepts_valid_formats(self):
        """Should accept valid format values."""
        # GIVEN valid formats
        for fmt in ("mp3", "wav", "pcm"):
            # WHEN creating config
            config = TTSConfig(format=fmt)
            # THEN it should work
            assert config.format == fmt

    def test_accepts_boundary_speeds(self):
        """Should accept speeds at boundaries."""
        # GIVEN boundary speeds
        for speed in (0.5, 2.0):
            # WHEN creating config
            config = TTSConfig(speed=speed)
            # THEN it should work
            assert config.speed == speed


class TestLoadConfig:
    """Tests for load_config function."""

    def test_returns_defaults_when_no_file(self, temp_config_dir):
        """Should return default config when file doesn't exist."""
        # GIVEN no config file
        # WHEN loading config
        config = load_config()

        # THEN defaults should be returned
        assert config.default_voice is None
        assert config.output_dir == "./audio_output"
        assert config.format == "mp3"
        assert config.speed == 1.0

    def test_loads_from_file(self, temp_config_dir):
        """Should load config from TOML file."""
        # GIVEN a config file
        config_file = temp_config_dir / "config.toml"
        config_file.write_text('''
default_voice = "voice-123"
output_dir = "/custom/output"
format = "wav"
speed = 1.5
''')

        # WHEN loading config
        config = load_config()

        # THEN values should be loaded
        assert config.default_voice == "voice-123"
        assert config.output_dir == "/custom/output"
        assert config.format == "wav"
        assert config.speed == 1.5

    def test_returns_defaults_on_invalid_toml(self, temp_config_dir):
        """Should return defaults if TOML is invalid."""
        # GIVEN invalid TOML
        config_file = temp_config_dir / "config.toml"
        config_file.write_text("this is not valid toml {{{")

        # WHEN loading config
        config = load_config()

        # THEN defaults should be returned
        assert config.format == "mp3"

    def test_ignores_unknown_fields(self, temp_config_dir):
        """Should ignore unknown config fields."""
        # GIVEN config with unknown field
        config_file = temp_config_dir / "config.toml"
        config_file.write_text('''
default_voice = "voice-123"
unknown_field = "ignored"
''')

        # WHEN loading config
        config = load_config()

        # THEN known field should be loaded
        assert config.default_voice == "voice-123"


class TestSaveConfig:
    """Tests for save_config function."""

    def test_creates_config_file(self, temp_config_dir):
        """Should create config file."""
        # GIVEN a config
        config = TTSConfig(default_voice="my-voice")

        # WHEN saving
        save_config(config)

        # THEN file should exist
        config_file = temp_config_dir / "config.toml"
        assert config_file.exists()

    def test_writes_all_values(self, temp_config_dir):
        """Should write all config values."""
        # GIVEN a config with custom values
        config = TTSConfig(
            default_voice="voice-456",
            output_dir="/my/output",
            format="wav",
            speed=1.5,
        )

        # WHEN saving
        save_config(config)

        # THEN all values should be written
        content = (temp_config_dir / "config.toml").read_text()
        assert 'default_voice = "voice-456"' in content
        assert 'output_dir = "/my/output"' in content
        assert 'format = "wav"' in content
        assert "speed = 1.5" in content

    def test_omits_none_default_voice(self, temp_config_dir):
        """Should not write default_voice if None."""
        # GIVEN a config with no default voice
        config = TTSConfig()

        # WHEN saving
        save_config(config)

        # THEN default_voice should not be in file
        content = (temp_config_dir / "config.toml").read_text()
        assert "default_voice" not in content


class TestUpdateConfig:
    """Tests for update_config function."""

    def test_updates_single_value(self, temp_config_dir):
        """Should update a single config value."""
        # GIVEN no existing config
        # WHEN updating format
        config = update_config(format="wav")

        # THEN format should be updated
        assert config.format == "wav"
        # AND other values should be defaults
        assert config.speed == 1.0

    def test_updates_multiple_values(self, temp_config_dir):
        """Should update multiple config values."""
        # GIVEN no existing config
        # WHEN updating multiple values
        config = update_config(format="pcm", speed=1.8)

        # THEN all should be updated
        assert config.format == "pcm"
        assert config.speed == 1.8

    def test_persists_changes(self, temp_config_dir):
        """Should persist changes to file."""
        # GIVEN an update
        update_config(default_voice="voice-789")

        # WHEN loading fresh
        config = load_config()

        # THEN change should persist
        assert config.default_voice == "voice-789"


class TestResetConfig:
    """Tests for reset_config function."""

    def test_resets_to_defaults(self, temp_config_dir):
        """Should reset config to defaults."""
        # GIVEN a custom config
        save_config(TTSConfig(format="wav", speed=1.8))

        # WHEN resetting
        config = reset_config()

        # THEN defaults should be restored
        assert config.format == "mp3"
        assert config.speed == 1.0

    def test_persists_reset(self, temp_config_dir):
        """Should persist the reset."""
        # GIVEN a custom config
        save_config(TTSConfig(format="wav"))

        # WHEN resetting and reloading
        reset_config()
        config = load_config()

        # THEN defaults should persist
        assert config.format == "mp3"
