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
    config_file = config_dir / "config.toml"

    # Patch in common module
    monkeypatch.setattr("tts.common.CONFIG_DIR", config_dir)
    monkeypatch.setattr("tts.common.CREDENTIALS_FILE", creds_file)

    # Patch in config module
    monkeypatch.setattr("tts.config.CONFIG_DIR", config_dir)
    monkeypatch.setattr("tts.config.CONFIG_FILE", config_file)

    # Patch in configure module (it imports these at module level)
    monkeypatch.setattr("tts.commands.configure.CONFIG_DIR", config_dir)
    monkeypatch.setattr("tts.commands.configure.CREDENTIALS_FILE", creds_file)
    monkeypatch.setattr("tts.commands.configure.CONFIG_FILE", config_file)

    return config_dir


@pytest.fixture
def mock_fish_client(mocker):
    """Mock the Fish Audio client."""
    mock_client = mocker.MagicMock()
    mocker.patch("tts.common.FishAudio", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_keyring_unavailable(mocker):
    """Mock keyring as unavailable."""
    mocker.patch("tts.common._keyring_available", return_value=False)
    mocker.patch("tts.commands.configure._keyring_available", return_value=False)


@pytest.fixture
def mock_keyring_available(mocker):
    """Mock keyring as available with in-memory storage."""
    storage = {}

    def mock_get(service, username):
        return storage.get(f"{service}:{username}")

    def mock_set(service, username, password):
        storage[f"{service}:{username}"] = password

    def mock_delete(service, username):
        key = f"{service}:{username}"
        if key in storage:
            del storage[key]

    mocker.patch("tts.common._keyring_available", return_value=True)
    mocker.patch("tts.commands.configure._keyring_available", return_value=True)

    # Patch keyring module in both locations
    mock_keyring = mocker.MagicMock()
    mock_keyring.get_password = mock_get
    mock_keyring.set_password = mock_set
    mock_keyring.delete_password = mock_delete

    mocker.patch.dict("sys.modules", {"keyring": mock_keyring})
    mocker.patch("tts.common.get_api_key_from_keyring", side_effect=lambda: mock_get("tts-cli", "api-key"))
    mocker.patch("tts.common.set_api_key_in_keyring", side_effect=lambda k: (mock_set("tts-cli", "api-key", k), True)[1])
    mocker.patch("tts.common.delete_api_key_from_keyring", side_effect=lambda: (mock_delete("tts-cli", "api-key"), True)[1])

    mocker.patch("tts.commands.configure.get_api_key_from_keyring", side_effect=lambda: mock_get("tts-cli", "api-key"))
    mocker.patch("tts.commands.configure.set_api_key_in_keyring", side_effect=lambda k: (mock_set("tts-cli", "api-key", k), True)[1])
    mocker.patch("tts.commands.configure.delete_api_key_from_keyring", side_effect=lambda: (mock_delete("tts-cli", "api-key"), True)[1])

    return storage
