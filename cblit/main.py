import click
import typer
from rich import print

from cblit.cli.session_wrapper import SessionWrapper
from cblit.gpt.country import ConstructedCountrySession

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def cli() -> None:
    """Cosmic Bureaucracy: Lost in Translation"""
    pass


def language() -> None:
    wrapper = SessionWrapper(ConstructedCountrySession)
    wrapper.run()


@app.command()
def start() -> None:
    """Start game command"""
    modes = click.Choice(["language", "officer"])
    mode = typer.prompt("Select mode", "language", show_choices=True, type=modes)
    if mode == "language":
        language()


if __name__ == "__main__":
    app()
