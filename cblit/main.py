import typer
from rich import print

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def cli() -> None:
    """Cosmic Bureaucracy: Lost in Translation"""
    pass


@app.command()
def start() -> None:
    """Start game command"""
    print("Game entrypoint")
    pass


if __name__ == "__main__":
    app()
