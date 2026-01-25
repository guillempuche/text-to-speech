"""Tests for main CLI application."""

import pytest

from tts import __version__
from tts.cli import app


class TestCLIHelp:
    """Test CLI help output."""

    def test_help_shows_all_commands(self, capsys):
        """Help should list all available commands."""
        # GIVEN the CLI app
        # WHEN help is requested
        with pytest.raises(SystemExit) as exc_info:
            app(["--help"])

        # THEN exit code should be 0
        assert exc_info.value.code == 0
        # AND all commands should be listed
        output = capsys.readouterr().out
        assert "generate" in output
        assert "configure" in output
        assert "update" in output
        assert "voice" in output

    def test_version_output(self, capsys):
        """Version flag should print current version."""
        # GIVEN the CLI app
        # WHEN version is requested
        with pytest.raises(SystemExit) as exc_info:
            app(["--version"])

        # THEN version should be displayed
        assert exc_info.value.code == 0
        output = capsys.readouterr().out
        assert __version__ in output


class TestSubcommandHelp:
    """Test help output for subcommands."""

    def test_generate_help(self, capsys):
        """Generate subcommand help should show options."""
        # GIVEN the CLI app
        # WHEN generate help is requested
        with pytest.raises(SystemExit) as exc_info:
            app(["generate", "--help"])

        # THEN exit code should be 0
        assert exc_info.value.code == 0
        # AND required parameters should be shown
        output = capsys.readouterr().out
        assert "reference-id" in output
        assert "output-dir" in output

    def test_configure_help(self, capsys):
        """Configure subcommand help should show usage."""
        # GIVEN the CLI app
        # WHEN configure help is requested
        with pytest.raises(SystemExit) as exc_info:
            app(["configure", "--help"])

        # THEN exit code should be 0
        assert exc_info.value.code == 0
        # AND API key parameter should be shown
        output = capsys.readouterr().out
        assert "API" in output.upper()

    def test_voice_help(self, capsys):
        """Voice subcommand help should show subcommands."""
        # GIVEN the CLI app
        # WHEN voice help is requested
        with pytest.raises(SystemExit) as exc_info:
            app(["voice", "--help"])

        # THEN exit code should be 0
        assert exc_info.value.code == 0
        # AND voice subcommands should be listed
        output = capsys.readouterr().out
        assert "upload" in output
        assert "list-models" in output
