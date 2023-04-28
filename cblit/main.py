import typer
from asyncio import run as aiorun
from cblit.game.game_cli_wrapper import GameCliWrapper

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def cli() -> None:
    """Cosmic Bureaucracy: Lost in Translation"""
    pass


@app.command()
def start() -> None:
    """Start game command"""
    async def _start() -> None:
        game_wrapper = GameCliWrapper()
        await game_wrapper.run()
    aiorun(_start())


if __name__ == "__main__":
    app()
