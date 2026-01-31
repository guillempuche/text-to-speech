"""Tests for voice management commands."""

import pytest

from tts.commands.voice import (
    find_audio_files,
    read_transcript,
    upload,
    list_models,
)


class TestFindAudioFiles:
    """Tests for find_audio_files utility."""

    def test_finds_supported_formats(self, tmp_path):
        """Should find all supported audio formats."""
        # GIVEN directory with various audio files
        for ext in [".wav", ".mp3", ".flac", ".ogg", ".m4a"]:
            (tmp_path / f"audio{ext}").write_text("fake")

        # WHEN find_audio_files is called
        result = find_audio_files(tmp_path)

        # THEN all audio files should be found
        assert len(result) == 5

    def test_ignores_non_audio_files(self, tmp_path):
        """Should ignore non-audio files."""
        # GIVEN directory with mixed files
        (tmp_path / "audio.wav").write_text("audio")
        (tmp_path / "text.txt").write_text("text")
        (tmp_path / "image.png").write_text("image")

        # WHEN find_audio_files is called
        result = find_audio_files(tmp_path)

        # THEN only audio files should be returned
        assert len(result) == 1
        assert result[0].suffix == ".wav"

    def test_returns_sorted_files(self, tmp_path):
        """Should return files in sorted order."""
        # GIVEN unsorted audio files
        (tmp_path / "z.wav").write_text("z")
        (tmp_path / "a.wav").write_text("a")
        (tmp_path / "m.wav").write_text("m")

        # WHEN find_audio_files is called
        result = find_audio_files(tmp_path)

        # THEN files should be sorted
        names = [f.name for f in result]
        assert names == ["a.wav", "m.wav", "z.wav"]

    def test_case_insensitive_extensions(self, tmp_path):
        """Should match extensions case-insensitively."""
        # GIVEN audio files with uppercase extensions
        (tmp_path / "upper.WAV").write_text("audio")
        (tmp_path / "mixed.Mp3").write_text("audio")

        # WHEN find_audio_files is called
        result = find_audio_files(tmp_path)

        # THEN both should be found
        assert len(result) == 2


class TestReadTranscript:
    """Tests for read_transcript utility."""

    def test_reads_companion_txt(self, tmp_path):
        """Should read .txt file with same stem as audio."""
        # GIVEN audio file and companion transcript
        audio_path = tmp_path / "sample.wav"
        audio_path.write_text("fake audio")
        (tmp_path / "sample.txt").write_text("This is the transcript.")

        # WHEN read_transcript is called
        result = read_transcript(audio_path)

        # THEN transcript content should be returned
        assert result == "This is the transcript."

    def test_returns_none_if_no_transcript(self, tmp_path):
        """Should return None if no companion .txt file."""
        # GIVEN audio file without transcript
        audio_path = tmp_path / "sample.wav"
        audio_path.write_text("fake audio")

        # WHEN read_transcript is called
        result = read_transcript(audio_path)

        # THEN None should be returned
        assert result is None

    def test_returns_none_for_empty_transcript(self, tmp_path, capsys):
        """Should return None and warn for empty transcript."""
        # GIVEN audio file with empty transcript
        audio_path = tmp_path / "sample.wav"
        audio_path.write_text("fake audio")
        (tmp_path / "sample.txt").write_text("")

        # WHEN read_transcript is called
        result = read_transcript(audio_path)

        # THEN None should be returned
        assert result is None
        # AND warning should be printed
        output = capsys.readouterr().out
        assert "empty" in output.lower()

    def test_strips_whitespace(self, tmp_path):
        """Should strip whitespace from transcript."""
        # GIVEN transcript with whitespace
        audio_path = tmp_path / "sample.wav"
        audio_path.write_text("fake audio")
        (tmp_path / "sample.txt").write_text("  spaced content  \n")

        # WHEN read_transcript is called
        result = read_transcript(audio_path)

        # THEN whitespace should be stripped
        assert result == "spaced content"


class TestUpload:
    """Tests for upload command."""

    def test_requires_api_key(self, tmp_path, capsys, monkeypatch):
        """Upload should fail without API key."""
        # GIVEN a directory with audio file and no credentials
        (tmp_path / "sample.wav").write_bytes(b"fake audio")
        monkeypatch.setattr("tts.common.CREDENTIALS_FILE", tmp_path / "nonexistent")
        monkeypatch.chdir(tmp_path)  # Ensure no .env in cwd

        # WHEN upload is called without API key
        with pytest.raises(SystemExit) as exc_info:
            upload(tmp_path, title="Test Voice")

        # THEN it should fail with API key error
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "FISH_API_KEY" in output

    def test_rejects_non_directory(self, tmp_path, monkeypatch, mocker, capsys):
        """Upload should fail for non-directory path."""
        # GIVEN a file path instead of directory
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mocker.patch("fishaudio.FishAudio")

        # WHEN upload is called with file path
        with pytest.raises(SystemExit) as exc_info:
            upload(file_path, title="Test")

        # THEN it should exit with error
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "not a directory" in output

    def test_exits_on_no_audio_files(self, tmp_path, monkeypatch, mocker, capsys):
        """Upload should exit when no audio files found."""
        # GIVEN empty directory
        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mocker.patch("fishaudio.FishAudio")

        # WHEN upload is called
        with pytest.raises(SystemExit) as exc_info:
            upload(tmp_path, title="Test")

        # THEN it should exit
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "No audio files" in output

    def test_uploads_with_transcripts(self, tmp_path, monkeypatch, mocker, capsys):
        """Upload should include transcripts when all files have them."""
        # GIVEN audio files with transcripts
        (tmp_path / "a.wav").write_bytes(b"audio1")
        (tmp_path / "a.txt").write_text("Transcript one")
        (tmp_path / "b.wav").write_bytes(b"audio2")
        (tmp_path / "b.txt").write_text("Transcript two")

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_client.voices.create.return_value = mocker.MagicMock(id="voice-123")
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN upload is called
        upload(tmp_path, title="Test Voice")

        # THEN voices.create should be called with texts
        call_kwargs = mock_client.voices.create.call_args[1]
        assert "texts" in call_kwargs
        assert len(call_kwargs["texts"]) == 2

    def test_ignores_partial_transcripts(self, tmp_path, monkeypatch, mocker, capsys):
        """Upload should ignore transcripts when only some files have them."""
        # GIVEN some audio files have transcripts
        (tmp_path / "a.wav").write_bytes(b"audio1")
        (tmp_path / "a.txt").write_text("Has transcript")
        (tmp_path / "b.wav").write_bytes(b"audio2")
        # b.txt is missing

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_client.voices.create.return_value = mocker.MagicMock(id="voice-123")
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN upload is called
        upload(tmp_path, title="Test Voice")

        # THEN warning should be shown
        output = capsys.readouterr().out
        assert "some files have transcripts" in output.lower()
        # AND texts should not be passed
        call_kwargs = mock_client.voices.create.call_args[1]
        assert "texts" not in call_kwargs

    def test_prints_voice_id_on_success(self, tmp_path, monkeypatch, mocker, capsys):
        """Upload should print voice ID on success."""
        # GIVEN audio file
        (tmp_path / "sample.wav").write_bytes(b"audio")

        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_client.voices.create.return_value = mocker.MagicMock(id="voice-abc123")
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN upload is called
        upload(tmp_path, title="Test Voice")

        # THEN voice ID should be printed
        output = capsys.readouterr().out
        assert "voice-abc123" in output


class TestListModels:
    """Tests for list_models command."""

    def test_requires_api_key(self, tmp_path, capsys, monkeypatch):
        """List models should fail without API key."""
        # GIVEN no API key and no credentials
        monkeypatch.setattr("tts.common.CREDENTIALS_FILE", tmp_path / "nonexistent")
        monkeypatch.chdir(tmp_path)  # Ensure no .env in cwd

        # WHEN list_models is called
        with pytest.raises(SystemExit) as exc_info:
            list_models()

        # THEN it should fail
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "FISH_API_KEY" in output

    def test_shows_no_models_message(self, monkeypatch, mocker, capsys):
        """List models should show message when no models found."""
        # GIVEN API returns empty paginated response
        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mock_result = mocker.MagicMock(items=[], total=0)
        mock_client.voices.list.return_value = mock_result
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN list_models is called
        list_models()

        # THEN no models message should be shown
        output = capsys.readouterr().out
        assert "No voice models" in output

    def test_lists_voice_models(self, monkeypatch, mocker, capsys):
        """List models should display voice models."""
        # GIVEN API returns voice models in paginated response
        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_voice1 = mocker.MagicMock(
            id="voice-1",
            title="Voice One",
            description="Description one",
            visibility="private",
            languages=["en"],
            tags=["male"],
            state="created",
            created_at="2025-01-01T00:00:00Z",
        )
        mock_voice2 = mocker.MagicMock(
            id="voice-2",
            title="Voice Two",
            description="",
            visibility="public",
            languages=[],
            tags=[],
            state="created",
            created_at="2025-01-02T00:00:00Z",
        )
        mock_result = mocker.MagicMock(items=[mock_voice1, mock_voice2], total=2)
        mock_client = mocker.MagicMock()
        mock_client.voices.list.return_value = mock_result
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN list_models is called
        list_models()

        # THEN voice models should be listed with details
        output = capsys.readouterr().out
        assert "voice-1" in output
        assert "Voice One" in output
        assert "voice-2" in output
        assert "Voice Two" in output
        assert "2 voice model(s)" in output
        # Should show additional details
        assert "Description one" in output
        assert "private" in output
        assert "en" in output
        assert "male" in output

    def test_uses_self_only_parameter(self, monkeypatch, mocker, capsys):
        """List models should use self_only=True to list only user's voices."""
        # GIVEN API setup
        monkeypatch.setenv("FISH_API_KEY", "test-key")
        mock_result = mocker.MagicMock(items=[], total=0)
        mock_client = mocker.MagicMock()
        mock_client.voices.list.return_value = mock_result
        mocker.patch("fishaudio.FishAudio", return_value=mock_client)

        # WHEN list_models is called
        list_models()

        # THEN API should be called with self_only=True
        mock_client.voices.list.assert_called_once_with(self_only=True, page_size=100)
