"""Tests for generate command."""

import pytest
from pathlib import Path

from tts.commands.generate import find_text_files, generate, _is_glob_pattern


class TestIsGlobPattern:
    """Tests for _is_glob_pattern utility."""

    def test_detects_asterisk(self):
        """Should detect * as glob pattern."""
        assert _is_glob_pattern("*.txt") is True
        assert _is_glob_pattern("**/*.txt") is True

    def test_detects_question_mark(self):
        """Should detect ? as glob pattern."""
        assert _is_glob_pattern("file?.txt") is True

    def test_detects_brackets(self):
        """Should detect [ as glob pattern."""
        assert _is_glob_pattern("file[0-9].txt") is True

    def test_normal_path_not_glob(self):
        """Should not detect normal paths as glob."""
        assert _is_glob_pattern("./path/to/file.txt") is False
        assert _is_glob_pattern("/absolute/path.txt") is False


class TestFindTextFiles:
    """Tests for find_text_files utility."""

    def test_returns_single_txt_file(self, tmp_path):
        """Should return single .txt file as list."""
        # GIVEN a single .txt file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")

        # WHEN find_text_files is called
        result = find_text_files(txt_file)

        # THEN it should return the file in a list
        assert result == [txt_file]

    def test_finds_txt_files_in_directory(self, tmp_path):
        """Should find all .txt files in a directory."""
        # GIVEN a directory with mixed files
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        (tmp_path / "c.md").write_text("c")
        (tmp_path / "d.py").write_text("d")

        # WHEN find_text_files is called
        result = find_text_files(tmp_path)

        # THEN only .txt files should be returned
        assert len(result) == 2
        assert all(f.suffix == ".txt" for f in result)

    def test_returns_sorted_files(self, tmp_path):
        """Should return files in sorted order."""
        # GIVEN unsorted .txt files
        (tmp_path / "z.txt").write_text("z")
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "m.txt").write_text("m")

        # WHEN find_text_files is called
        result = find_text_files(tmp_path)

        # THEN files should be sorted
        names = [f.name for f in result]
        assert names == ["a.txt", "m.txt", "z.txt"]

    def test_rejects_non_txt_file(self, tmp_path):
        """Should exit when given a non-.txt file."""
        # GIVEN a non-.txt file
        other_file = tmp_path / "test.md"
        other_file.write_text("content")

        # WHEN find_text_files is called
        # THEN it should exit with error
        with pytest.raises(SystemExit) as exc_info:
            find_text_files(other_file)
        assert exc_info.value.code == 1

    def test_handles_empty_directory(self, tmp_path):
        """Should return empty list for directory with no .txt files."""
        # GIVEN an empty directory
        # WHEN find_text_files is called
        result = find_text_files(tmp_path)

        # THEN empty list should be returned
        assert result == []

    def test_glob_pattern_asterisk(self, tmp_path, monkeypatch):
        """Should support *.txt glob pattern."""
        # GIVEN multiple .txt files
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        (tmp_path / "c.md").write_text("c")
        monkeypatch.chdir(tmp_path)

        # WHEN using glob pattern
        result = find_text_files("*.txt")

        # THEN only .txt files should be returned
        assert len(result) == 2
        names = [f.name for f in result]
        assert "a.txt" in names
        assert "b.txt" in names

    def test_glob_pattern_recursive(self, tmp_path, monkeypatch):
        """Should support **/*.txt recursive glob pattern."""
        # GIVEN nested .txt files
        (tmp_path / "root.txt").write_text("root")
        subdir = tmp_path / "sub"
        subdir.mkdir()
        (subdir / "nested.txt").write_text("nested")
        monkeypatch.chdir(tmp_path)

        # WHEN using recursive glob pattern
        result = find_text_files("**/*.txt")

        # THEN all .txt files should be found
        names = [f.name for f in result]
        assert "nested.txt" in names

    def test_glob_pattern_subdir(self, tmp_path, monkeypatch):
        """Should support subdirectory glob pattern."""
        # GIVEN files in subdirectory
        subdir = tmp_path / "scripts"
        subdir.mkdir()
        (subdir / "script1.txt").write_text("1")
        (subdir / "script2.txt").write_text("2")
        (tmp_path / "other.txt").write_text("other")
        monkeypatch.chdir(tmp_path)

        # WHEN using subdir glob pattern
        result = find_text_files("scripts/*.txt")

        # THEN only subdir files should be returned
        assert len(result) == 2
        names = [f.name for f in result]
        assert "script1.txt" in names
        assert "other.txt" not in names


class TestGenerate:
    """Tests for generate command."""

    def test_requires_api_key(self, tmp_path, capsys, monkeypatch):
        """Generate should fail without API key."""
        # GIVEN a text file exists and no credentials
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello world")
        nonexistent = tmp_path / "nonexistent"
        monkeypatch.setattr("tts.common.CREDENTIALS_FILE", nonexistent)
        monkeypatch.setattr("tts.common._keyring_available", lambda: False)
        # Also patch where it's used in generate (via load_api_key)
        monkeypatch.chdir(tmp_path)  # Ensure no .env in cwd

        # WHEN generate is called without API key
        with pytest.raises(SystemExit) as exc_info:
            generate(
                str(text_file),
                reference_id="voice-123",
                output_dir=tmp_path / "output",
            )

        # THEN it should fail with error about API key
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "FISH_API_KEY" in output

    def test_requires_reference_id(self, tmp_path, monkeypatch, mocker, capsys):
        """Generate should fail without reference_id."""
        # GIVEN a text file and API key but no reference_id
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello world")

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # AND no default voice configured
        config_file = tmp_path / "config.toml"
        monkeypatch.setattr("tts.config.CONFIG_FILE", config_file)

        # WHEN generate is called without reference_id
        with pytest.raises(SystemExit) as exc_info:
            generate(str(text_file))

        # THEN it should fail
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "reference-id" in output.lower()

    def test_processes_single_file(self, tmp_path, monkeypatch, mocker, capsys):
        """Generate should process a single text file."""
        # GIVEN a text file and API key
        text_file = tmp_path / "hello.txt"
        text_file.write_text("Hello, this is a test.")
        output_dir = tmp_path / "output"

        monkeypatch.setenv("FISH_API_KEY", "test-key")

        # AND Fish client is mocked
        mock_client = mocker.MagicMock()
        mock_client.tts.convert.return_value = b"fake-audio-data"
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN generate is called
        generate(
            str(text_file),
            reference_id="voice-123",
            output_dir=output_dir,
        )

        # THEN API should be called correctly
        mock_client.tts.convert.assert_called_once()
        call_kwargs = mock_client.tts.convert.call_args[1]
        assert call_kwargs["text"] == "Hello, this is a test."
        assert call_kwargs["reference_id"] == "voice-123"
        # AND output file should be created
        assert (output_dir / "hello.mp3").exists()

    def test_skips_empty_files(self, tmp_path, monkeypatch, mocker, capsys):
        """Generate should skip empty text files."""
        # GIVEN an empty file
        text_file = tmp_path / "empty.txt"
        text_file.write_text("")

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN generate is called
        generate(
            str(text_file),
            reference_id="voice-123",
            output_dir=tmp_path / "output",
        )

        # THEN API should not be called
        mock_client.tts.convert.assert_not_called()
        # AND skip message should be shown
        output = capsys.readouterr().out
        assert "Skipping" in output

    def test_rejects_invalid_speed(self, tmp_path, monkeypatch, mocker, capsys):
        """Generate should reject speed outside valid range."""
        # GIVEN a text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("content")

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN generate is called with invalid speed
        # THEN it should exit with error
        with pytest.raises(SystemExit) as exc_info:
            generate(
                str(text_file),
                reference_id="voice-123",
                speed=3.0,  # Invalid: > 2.0
            )

        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "speed" in output.lower()

    def test_exits_on_no_txt_files(self, tmp_path, monkeypatch, mocker, capsys):
        """Generate should exit when no .txt files found."""
        # GIVEN an empty directory
        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mocker.patch("fishaudio.FishAudio")

        # WHEN generate is called
        # THEN it should exit
        with pytest.raises(SystemExit) as exc_info:
            generate(
                str(tmp_path),
                reference_id="voice-123",
            )

        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "No .txt files" in output

    def test_creates_output_directory(self, tmp_path, monkeypatch, mocker):
        """Generate should create output directory if missing."""
        # GIVEN a text file and non-existent output dir
        text_file = tmp_path / "test.txt"
        text_file.write_text("content")
        output_dir = tmp_path / "nested" / "output"

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_client.tts.convert.return_value = b"audio"
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN generate is called
        generate(
            str(text_file),
            reference_id="voice-123",
            output_dir=output_dir,
        )

        # THEN output directory should be created
        assert output_dir.exists()

    def test_uses_specified_format(self, tmp_path, monkeypatch, mocker):
        """Generate should use the specified output format."""
        # GIVEN a text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("content")
        output_dir = tmp_path / "output"

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_client.tts.convert.return_value = b"audio"
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN generate is called with wav format
        generate(
            str(text_file),
            reference_id="voice-123",
            format="wav",
            output_dir=output_dir,
        )

        # THEN output should have .wav extension
        assert (output_dir / "test.wav").exists()
        # AND API should be called with wav format
        call_kwargs = mock_client.tts.convert.call_args[1]
        assert call_kwargs["format"] == "wav"

    def test_uses_config_defaults(self, tmp_path, monkeypatch, mocker):
        """Generate should use config defaults when options not specified."""
        # GIVEN a text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("content")

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_client.tts.convert.return_value = b"audio"
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # AND config has custom defaults
        config_dir = tmp_path / ".config" / "tts"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.toml"
        config_file.write_text('''
default_voice = "config-voice"
output_dir = "./config_output"
format = "wav"
speed = 1.5
''')
        monkeypatch.setattr("tts.config.CONFIG_FILE", config_file)
        monkeypatch.setattr("tts.commands.generate.load_config", lambda: __import__("tts.config", fromlist=["load_config"]).load_config())

        # Force reload config
        from tts.config import load_config
        monkeypatch.setattr("tts.config.CONFIG_FILE", config_file)

        # WHEN generate is called without options
        generate(str(text_file))

        # THEN config defaults should be used
        call_kwargs = mock_client.tts.convert.call_args[1]
        assert call_kwargs["reference_id"] == "config-voice"
        assert call_kwargs["format"] == "wav"
        assert call_kwargs["speed"] == 1.5

    def test_cli_options_override_config(self, tmp_path, monkeypatch, mocker):
        """CLI options should override config defaults."""
        # GIVEN a text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("content")
        output_dir = tmp_path / "cli_output"

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_client.tts.convert.return_value = b"audio"
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # AND config has defaults
        config_dir = tmp_path / ".config" / "tts"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "config.toml"
        config_file.write_text('''
default_voice = "config-voice"
format = "wav"
speed = 1.5
''')
        monkeypatch.setattr("tts.config.CONFIG_FILE", config_file)

        # WHEN generate is called with explicit options
        generate(
            str(text_file),
            reference_id="cli-voice",
            format="pcm",
            speed=0.8,
            output_dir=output_dir,
        )

        # THEN CLI options should be used
        call_kwargs = mock_client.tts.convert.call_args[1]
        assert call_kwargs["reference_id"] == "cli-voice"
        assert call_kwargs["format"] == "pcm"
        assert call_kwargs["speed"] == 0.8
