"""Tests for shared utilities."""

import os
import pytest
from pathlib import Path

from tts.common import load_env_file, load_api_key, require_api_key


class TestLoadEnvFile:
    """Tests for load_env_file function."""

    def test_loads_key_value_pairs(self, tmp_path, monkeypatch):
        """Should load KEY=VALUE pairs into os.environ."""
        # GIVEN an env file with key-value pairs
        env_file = tmp_path / ".env"
        env_file.write_text("MY_KEY=my_value\nOTHER_KEY=other_value\n")
        monkeypatch.delenv("MY_KEY", raising=False)
        monkeypatch.delenv("OTHER_KEY", raising=False)

        # WHEN load_env_file is called
        load_env_file(env_file)

        # THEN environment variables should be set
        assert os.environ.get("MY_KEY") == "my_value"
        assert os.environ.get("OTHER_KEY") == "other_value"

    def test_ignores_comments(self, tmp_path, monkeypatch):
        """Should ignore lines starting with #."""
        # GIVEN an env file with comments
        env_file = tmp_path / ".env"
        env_file.write_text("# This is a comment\nVALID_KEY=valid_value\n")
        monkeypatch.delenv("VALID_KEY", raising=False)

        # WHEN load_env_file is called
        load_env_file(env_file)

        # THEN only non-comment lines should be loaded
        assert os.environ.get("VALID_KEY") == "valid_value"

    def test_ignores_empty_lines(self, tmp_path, monkeypatch):
        """Should skip empty lines."""
        # GIVEN an env file with empty lines
        env_file = tmp_path / ".env"
        env_file.write_text("\n\nKEY=value\n\n")
        monkeypatch.delenv("KEY", raising=False)

        # WHEN load_env_file is called
        load_env_file(env_file)

        # THEN key should still be loaded
        assert os.environ.get("KEY") == "value"

    def test_strips_quotes(self, tmp_path, monkeypatch):
        """Should strip quotes from values."""
        # GIVEN an env file with quoted values
        env_file = tmp_path / ".env"
        env_file.write_text('DOUBLE="double_quoted"\nSINGLE=\'single_quoted\'\n')
        monkeypatch.delenv("DOUBLE", raising=False)
        monkeypatch.delenv("SINGLE", raising=False)

        # WHEN load_env_file is called
        load_env_file(env_file)

        # THEN quotes should be stripped
        assert os.environ.get("DOUBLE") == "double_quoted"
        assert os.environ.get("SINGLE") == "single_quoted"

    def test_does_not_override_existing(self, tmp_path, monkeypatch):
        """Should not override existing environment variables."""
        # GIVEN an existing environment variable
        monkeypatch.setenv("EXISTING", "original")
        env_file = tmp_path / ".env"
        env_file.write_text("EXISTING=overwritten\n")

        # WHEN load_env_file is called
        load_env_file(env_file)

        # THEN existing value should remain
        assert os.environ.get("EXISTING") == "original"

    def test_exits_on_read_error(self, tmp_path):
        """Should exit when file cannot be read."""
        # GIVEN a non-existent file
        missing_file = tmp_path / "missing.env"

        # WHEN load_env_file is called
        # THEN it should exit with error
        with pytest.raises(SystemExit) as exc_info:
            load_env_file(missing_file)
        assert exc_info.value.code == 1


class TestLoadApiKey:
    """Tests for load_api_key function."""

    def test_does_nothing_if_already_set(self, monkeypatch, tmp_path):
        """Should return early if FISH_API_KEY is already in environment."""
        # GIVEN FISH_API_KEY is set
        monkeypatch.setenv("FISH_API_KEY", "existing-key")

        # WHEN load_api_key is called
        load_api_key()

        # THEN the existing key should remain
        assert os.environ.get("FISH_API_KEY") == "existing-key"

    def test_loads_from_credentials_file(self, temp_config_dir, monkeypatch):
        """Should load API key from credentials file."""
        # GIVEN credentials file exists with API key
        creds_file = temp_config_dir / "credentials"
        creds_file.write_text("FISH_API_KEY=creds-key\n")

        # WHEN load_api_key is called
        load_api_key()

        # THEN key should be loaded
        assert os.environ.get("FISH_API_KEY") == "creds-key"

    def test_loads_from_env_file(self, tmp_path, monkeypatch):
        """Should load API key from specified .env file."""
        # GIVEN a .env file with API key
        env_file = tmp_path / "custom.env"
        env_file.write_text("FISH_API_KEY=env-file-key\n")
        monkeypatch.setattr("tts.common.CREDENTIALS_FILE", tmp_path / "nonexistent")

        # WHEN load_api_key is called with env_file
        load_api_key(env_file=env_file)

        # THEN key should be loaded
        assert os.environ.get("FISH_API_KEY") == "env-file-key"

    def test_exits_if_env_file_missing(self, tmp_path, monkeypatch):
        """Should exit if specified env file doesn't exist."""
        # GIVEN a non-existent env file path
        missing_file = tmp_path / "missing.env"
        monkeypatch.setattr("tts.common.CREDENTIALS_FILE", tmp_path / "nonexistent")

        # WHEN load_api_key is called with missing file
        # THEN it should exit
        with pytest.raises(SystemExit) as exc_info:
            load_api_key(env_file=missing_file)
        assert exc_info.value.code == 1


class TestRequireApiKey:
    """Tests for require_api_key function."""

    def test_passes_when_key_set(self, monkeypatch):
        """Should not exit when API key is set."""
        # GIVEN FISH_API_KEY is set
        monkeypatch.setenv("FISH_API_KEY", "valid-key")

        # WHEN require_api_key is called
        # THEN no exception should be raised
        require_api_key()  # Should not raise

    def test_exits_when_key_missing(self, monkeypatch, capsys):
        """Should exit with helpful message when key is missing."""
        # GIVEN FISH_API_KEY is not set
        monkeypatch.delenv("FISH_API_KEY", raising=False)

        # WHEN require_api_key is called
        # THEN it should exit with instructions
        with pytest.raises(SystemExit) as exc_info:
            require_api_key()

        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "FISH_API_KEY" in output
        assert "configure" in output
