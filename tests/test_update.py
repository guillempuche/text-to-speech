"""Tests for update command."""

from pathlib import Path
import pytest

from tts.commands.update import (
    get_platform_binary,
    parse_version,
    fetch_latest_release,
    get_binary_path,
    fetch_checksums,
    verify_checksum,
    update,
)


class TestGetPlatformBinary:
    """Tests for platform binary name detection."""

    def test_macos_arm64(self, mocker):
        """Should return arm64 binary for Apple Silicon."""
        # GIVEN macOS ARM64 platform
        mocker.patch("platform.system", return_value="Darwin")
        mocker.patch("platform.machine", return_value="arm64")

        # WHEN get_platform_binary is called
        result = get_platform_binary()

        # THEN arm64 binary should be returned
        assert result == "tts-macos-arm64"

    def test_macos_x64(self, mocker):
        """Should return x64 binary for Intel Mac."""
        # GIVEN macOS x64 platform
        mocker.patch("platform.system", return_value="Darwin")
        mocker.patch("platform.machine", return_value="x86_64")

        # WHEN get_platform_binary is called
        result = get_platform_binary()

        # THEN x64 binary should be returned
        assert result == "tts-macos-x64"

    def test_linux_x64(self, mocker):
        """Should return Linux x64 binary."""
        # GIVEN Linux platform
        mocker.patch("platform.system", return_value="Linux")
        mocker.patch("platform.machine", return_value="x86_64")

        # WHEN get_platform_binary is called
        result = get_platform_binary()

        # THEN Linux binary should be returned
        assert result == "tts-linux-x64"

    def test_windows_x64(self, mocker):
        """Should return Windows binary with .exe extension."""
        # GIVEN Windows platform
        mocker.patch("platform.system", return_value="Windows")
        mocker.patch("platform.machine", return_value="AMD64")

        # WHEN get_platform_binary is called
        result = get_platform_binary()

        # THEN Windows binary with .exe should be returned
        assert result == "tts-windows-x64.exe"


class TestParseVersion:
    """Tests for version parsing."""

    def test_parses_calver(self):
        """Should parse calver version string."""
        # GIVEN a calver version
        # WHEN parse_version is called
        result = parse_version("2025.01.25")

        # THEN tuple should be returned
        assert result == (2025, 1, 25)

    def test_strips_v_prefix(self):
        """Should strip v prefix from version."""
        # GIVEN version with v prefix
        # WHEN parse_version is called
        result = parse_version("v2025.01.25")

        # THEN tuple without prefix should be returned
        assert result == (2025, 1, 25)

    def test_handles_invalid_parts(self):
        """Should convert invalid parts to 0."""
        # GIVEN version with invalid parts
        # WHEN parse_version is called
        result = parse_version("2025.abc.01")

        # THEN invalid parts should be 0
        assert result == (2025, 0, 1)

    def test_supports_comparison(self):
        """Parsed versions should be comparable."""
        # GIVEN two versions
        v1 = parse_version("2025.01.01")
        v2 = parse_version("2025.01.25")

        # THEN they should be comparable
        assert v1 < v2
        assert v2 > v1


class TestFetchLatestRelease:
    """Tests for GitHub API fetch."""

    def test_returns_none_on_network_error(self, mocker):
        """Should return None when network fails."""
        # GIVEN network is unavailable
        mocker.patch(
            "urllib.request.urlopen",
            side_effect=Exception("Network error"),
        )

        # WHEN fetch_latest_release is called
        result = fetch_latest_release()

        # THEN None should be returned
        assert result is None

    def test_returns_release_data(self, mocker):
        """Should return release data on success."""
        # GIVEN API returns release data
        mock_response = mocker.MagicMock()
        mock_response.read.return_value = b'{"tag_name": "v2025.01.30"}'
        mock_response.__enter__ = mocker.MagicMock(return_value=mock_response)
        mock_response.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch("urllib.request.urlopen", return_value=mock_response)

        # WHEN fetch_latest_release is called
        result = fetch_latest_release()

        # THEN release data should be returned
        assert result == {"tag_name": "v2025.01.30"}


class TestUpdate:
    """Tests for update command."""

    def test_shows_current_version(self, mocker, capsys):
        """Update should show current version."""
        # GIVEN API returns newer version
        mocker.patch(
            "tts.commands.update.fetch_latest_release",
            return_value={"tag_name": "v2099.01.01"},
        )

        # WHEN update is called
        update()

        # THEN current version should be shown
        output = capsys.readouterr().out
        assert "Current version" in output

    def test_shows_up_to_date_message(self, mocker, capsys):
        """Update should indicate when up to date."""
        # GIVEN API returns same or older version
        mocker.patch(
            "tts.commands.update.fetch_latest_release",
            return_value={"tag_name": "v2020.01.01"},
        )

        # WHEN update is called
        update()

        # THEN up to date message should be shown
        output = capsys.readouterr().out
        assert "up to date" in output.lower()

    def test_shows_pip_instructions_when_not_binary(self, mocker, capsys):
        """Update should show pip install instructions when not running as binary."""
        # GIVEN API returns newer version and not running as binary
        mocker.patch(
            "tts.commands.update.fetch_latest_release",
            return_value={"tag_name": "v2099.01.01"},
        )
        mocker.patch("tts.commands.update.get_binary_path", return_value=None)

        # WHEN update is called (not check-only)
        update(check=False)

        # THEN pip install instructions should be shown
        output = capsys.readouterr().out
        assert "pip install --upgrade" in output
        assert "download binary" in output.lower()

    def test_check_only_skips_download_instructions(self, mocker, capsys):
        """Update with --check should skip download instructions."""
        # GIVEN API returns newer version
        mocker.patch(
            "tts.commands.update.fetch_latest_release",
            return_value={"tag_name": "v2099.01.01"},
        )

        # WHEN update is called with check=True
        update(check=True)

        # THEN download instructions should not be shown
        output = capsys.readouterr().out
        assert "Download" not in output
        assert "New version available" in output

    def test_exits_on_fetch_failure(self, mocker, capsys):
        """Update should exit when cannot fetch release info."""
        # GIVEN API fetch fails
        mocker.patch("tts.commands.update.fetch_latest_release", return_value=None)

        # WHEN update is called
        # THEN it should exit with error
        with pytest.raises(SystemExit) as exc_info:
            update()

        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "Could not fetch" in output


class TestGetBinaryPath:
    """Tests for binary path detection."""

    def test_returns_none_when_pyapp_not_set(self, mocker):
        """Should return None when PYAPP env var is not set."""
        # GIVEN PYAPP is not set
        mocker.patch.dict("os.environ", {}, clear=True)

        # WHEN get_binary_path is called
        result = get_binary_path()

        # THEN None should be returned
        assert result is None

    def test_returns_path_when_pyapp_set(self, mocker):
        """Should return path when PYAPP env var is set."""
        # GIVEN PYAPP is set and sys.executable points to binary
        mocker.patch.dict("os.environ", {"PYAPP": "1"})
        mocker.patch("sys.executable", "/usr/local/bin/tts")

        # WHEN get_binary_path is called
        result = get_binary_path()

        # THEN binary path should be returned
        assert result == Path("/usr/local/bin/tts")

    def test_returns_path_for_windows_binary(self, mocker):
        """Should return path for Windows tts.exe binary."""
        # GIVEN PYAPP is set and sys.executable points to tts.exe
        mocker.patch.dict("os.environ", {"PYAPP": "1"})
        mocker.patch("sys.executable", "C:\\Program Files\\tts\\tts.exe")

        # WHEN get_binary_path is called
        result = get_binary_path()

        # THEN binary path should be returned
        assert result == Path("C:\\Program Files\\tts\\tts.exe")


class TestFetchChecksums:
    """Tests for checksum fetching."""

    def test_parses_checksums_file(self, mocker):
        """Should parse checksums.txt format."""
        # GIVEN checksums file content
        content = b"abc123  tts-linux-x64\ndef456  tts-macos-arm64"
        mock_response = mocker.MagicMock()
        mock_response.read.return_value = content
        mock_response.__enter__ = mocker.MagicMock(return_value=mock_response)
        mock_response.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch("urllib.request.urlopen", return_value=mock_response)

        # WHEN fetch_checksums is called
        result = fetch_checksums("v2025.01.01")

        # THEN checksums should be parsed
        assert result == {
            "tts-linux-x64": "abc123",
            "tts-macos-arm64": "def456",
        }

    def test_returns_empty_on_network_error(self, mocker):
        """Should return empty dict on network error."""
        # GIVEN network error
        mocker.patch("urllib.request.urlopen", side_effect=Exception("Network error"))

        # WHEN fetch_checksums is called
        result = fetch_checksums("v2025.01.01")

        # THEN empty dict should be returned
        assert result == {}


class TestVerifyChecksum:
    """Tests for checksum verification."""

    def test_verifies_correct_checksum(self, tmp_path):
        """Should return True for correct checksum."""
        # GIVEN a file with known content
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"hello world")
        # SHA256 of "hello world"
        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

        # WHEN verify_checksum is called
        result = verify_checksum(test_file, expected)

        # THEN True should be returned
        assert result is True

    def test_rejects_incorrect_checksum(self, tmp_path):
        """Should return False for incorrect checksum."""
        # GIVEN a file with known content
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"hello world")

        # WHEN verify_checksum is called with wrong hash
        result = verify_checksum(test_file, "wronghash")

        # THEN False should be returned
        assert result is False
