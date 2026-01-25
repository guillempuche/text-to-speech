"""Main CLI application with subcommands."""

import cyclopts

from tts import __version__
from tts.commands import configure, generate, update, voice

app = cyclopts.App(
    name="tts",
    help="Text-to-speech CLI for Fish Audio.",
    version=__version__,
)

# Register subcommands
app.command(generate.generate)
app.command(configure.app, name="configure")
app.command(update.update)
app.command(voice.app, name="voice")


def main() -> None:
    """Entry point for the CLI."""
    app()
