import dataclasses
import datetime
import glob
import os
from typing import Callable, Dict, Optional
from rich import print

import click
import typer

from cblit.game.game import Game

LOG_DIRECTORY = os.path.join(os.getcwd(), os.pardir, "gpt-logs")


@dataclasses.dataclass
class GameCliMode:
    name: str
    method: Callable[[], None]


class GameCliWrapper:
    game: Optional[Game]
    modes: Dict[str, GameCliMode]

    def __init__(self, game: Optional[Game] = None) -> None:
        self.game = game
        self.detect_modes()

    def detect_modes(self) -> None:
        self.modes = {
            "n": GameCliMode("New game", self.generate)
        }

        if self.game is not None:
            self.modes.update({
                "p": GameCliMode("Pretty print game", self.print),
                "s": GameCliMode("Save game", self.save),
                "l": GameCliMode("Load game", self.load),
            })

    def generate(self) -> None:
        self.game = Game.generate()
        self.detect_modes()

    def print(self) -> None:
        print(self.game)

    def save(self) -> None:
        filename = f"Game-{datetime.datetime.now().isoformat()}.json"
        filename = typer.prompt("Enter filename to save the log file", default=filename)
        self._save(os.path.join(LOG_DIRECTORY, filename))
        print(f"[green]Game file is saved: {filename}[/green]")

    def _save(self, destination: str) -> None:
        if self.game is None:
            raise ValueError("Game has not been started, cannot save")
        game_json = self.game.to_json(indent=2)
        with open(destination, "w") as f:
            f.write(game_json)

    def load(self) -> None:
        print("Select file to load:")
        paths = glob.glob(os.path.join(LOG_DIRECTORY, "*.json"))
        for i, path in enumerate(paths):
            print(f"  {i}) {os.path.basename(path)}")
        choice = typer.prompt("File index", type=click.Choice([str(i) for i in range(len(paths))]))
        source = paths[int(choice)]
        self._load(source)
        print(f"[green]Game file is loaded: {os.path.basename(source)}[/green]")

    def _load(self, source: str) -> None:
        with open(source, "r") as f:
            self.game = Game.from_json(f.read())

    def run(self) -> None:
        while True:
            try:
                prompt = "Select mode:\n"
                for (key, mode) in self.modes.items():
                    prompt += f" {key}) {mode.name}\n"
                prompt += "> "
                choice_labels = list(self.modes.keys())
                choice = typer.prompt(prompt, type=click.Choice(choice_labels))
                method = self.modes[choice].method
                method()
            except click.exceptions.Abort:
                print("[yellow]Done[/yellow]")
                return
