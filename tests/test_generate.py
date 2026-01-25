"""Tests for generate command."""

import pytest
from pathlib import Path

from tts.commands.generate import find_text_files, generate


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


class TestGenerate:
    """Tests for generate command."""

    def test_requires_api_key(self, tmp_path, capsys, monkeypatch):
        """Generate should fail without API key."""
        # GIVEN a text file exists and no credentials
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello world")
        nonexistent = tmp_path / "nonexistent"
        monkeypatch.setattr("tts.common.CREDENTIALS_FILE", nonexistent)
        # Also patch where it's used in generate (via load_api_key)
        monkeypatch.chdir(tmp_path)  # Ensure no .env in cwd

        # WHEN generate is called without API key
        with pytest.raises(SystemExit) as exc_info:
            generate(
                text_file,
                reference_id="voice-123",
                output_dir=tmp_path / "output",
            )

        # THEN it should fail with error about API key
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "FISH_API_KEY" in output

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
            text_file,
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
            text_file,
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
                text_file,
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
                tmp_path,
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
            text_file,
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
            text_file,
            reference_id="voice-123",
            format="wav",
            output_dir=output_dir,
        )

        # THEN output should have .wav extension
        assert (output_dir / "test.wav").exists()
        # AND API should be called with wav format
        call_kwargs = mock_client.tts.convert.call_args[1]
        assert call_kwargs["format"] == "wav"
