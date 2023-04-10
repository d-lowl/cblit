import typer

from cblit.game.game_cli_wrapper import GameCliWrapper

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def cli() -> None:
    """Cosmic Bureaucracy: Lost in Translation"""
    pass


@app.command()
def start() -> None:
    """Start game command"""
    game_wrapper = GameCliWrapper()
    game_wrapper.run()


if __name__ == "__main__":
    app()
