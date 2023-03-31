import click
import typer

from cblit.cli.session_wrapper import SessionWrapper
from cblit.gpt.country import ConstructedCountrySession
from cblit.gpt.officer import OfficerSession

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def cli() -> None:
    """Cosmic Bureaucracy: Lost in Translation"""
    pass


def language() -> None:
    wrapper = SessionWrapper(ConstructedCountrySession)
    wrapper.run()


def officer() -> None:
    wrapper = SessionWrapper(OfficerSession)
    wrapper.run()


@app.command()
def start() -> None:
    """Start game command"""
    modes = click.Choice(["language", "officer"])
    mode = typer.prompt("Select mode", "officer", show_choices=True, type=modes)
    if mode == "language":
        language()
    elif mode == "officer":
        officer()


if __name__ == "__main__":
    app()
