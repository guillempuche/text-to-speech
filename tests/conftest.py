"""Shared test fixtures for TTS CLI tests."""

import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure API key is not set from environment."""
    monkeypatch.delenv("FISH_API_KEY", raising=False)


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Override config directory to temp path in all modules."""
    config_dir = tmp_path / ".config" / "tts"
    config_dir.mkdir(parents=True)
    creds_file = config_dir / "credentials"

    # Patch in common module
    monkeypatch.setattr("tts.common.CONFIG_DIR", config_dir)
    monkeypatch.setattr("tts.common.CREDENTIALS_FILE", creds_file)

    # Patch in configure module (it imports these at module level)
    monkeypatch.setattr("tts.commands.configure.CONFIG_DIR", config_dir)
    monkeypatch.setattr("tts.commands.configure.CREDENTIALS_FILE", creds_file)

    return config_dir


@pytest.fixture
def mock_fish_client(mocker):
    """Mock the Fish Audio client."""
    mock_client = mocker.MagicMock()
    mocker.patch("tts.common.FishAudio", return_value=mock_client)
    return mock_client
