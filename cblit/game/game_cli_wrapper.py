import dataclasses
import datetime
import glob
import os
from collections.abc import Callable, Coroutine
from typing import Any, TypeAlias

import click
import typer
from rich import print

from cblit.cli.session_wrapper import SessionMethodWrapper, SessionWrapper
from cblit.game.game import Game

LOG_DIRECTORY = os.path.join(os.getcwd(), os.pardir, "gpt-logs")

GameMethod: TypeAlias = Callable[[], None] | Callable[[], Coroutine[Any, Any, None]]


@dataclasses.dataclass
class GameCliMode:
    name: str
    method: GameMethod


class GameCliWrapper:
    _game: Game | None
    modes: dict[str, GameCliMode]

    @property
    def game(self) -> Game:
        if self._game is None:
            raise ValueError("Game is not initialised")
        return self._game

    def __init__(self, game: Game | None = None) -> None:
        self._game = game
        self.detect_modes()

    def detect_modes(self) -> None:
        self.modes = {
            "n": GameCliMode("New game", self.generate),
            "l": GameCliMode("Load game", self.load)
        }

        if self._game is not None:
            self.modes.update({
                "p": GameCliMode("Pretty print game", self.print),
                "s": GameCliMode("Save game", self.save),
                "ic": GameCliMode("Inspect country session", self.inspect_country),
                "io": GameCliMode("Inspect officer session", self.inspect_officer),
                "t": GameCliMode("Talk to officer", self.talk),
                "b": GameCliMode("Show phrasebook", self.show_phrasebook),
                "g": GameCliMode("Give document", self.give_document)
            })

    async def generate(self) -> None:
        self._game = await Game.generate()
        self.detect_modes()
        reply: str = await self.game.start()
        print(f"<: {reply}")

    def print(self) -> None:
        print(self.game)

    async def inspect_country(self) -> None:
        await SessionWrapper.from_session(self.game.country_session).run()

    async def inspect_officer(self) -> None:
        raise NotImplementedError()
        # await SessionWrapper.from_session(self.game.officer_session).run()

    async def talk(self) -> None:
        async def wrap_say_to_officer(sentence: str, priority: int) -> str:
            return await self.game.say_to_officer(sentence, "hard")

        wrapper = SessionMethodWrapper("say_to_officer", wrap_say_to_officer)
        await wrapper.run()

    def show_phrasebook(self) -> None:
        for phrase in self.game.phrasebook.phrases:
            print(f"{phrase.english} -> {phrase.conlang}")

    def give_document(self) -> None:
        try:
            print("Select document to give:")
            for i, document in enumerate(self.game.immigrant.documents):
                print(i, document.player_representation, "\n")
            choice_labels = [str(x) for x in range(len(self.game.immigrant.documents))]
            choice = typer.prompt("> ", type=click.Choice(choice_labels))
            reply = self.game.give_document(int(choice), "hard")
            print(f"<: {reply}")
        except click.exceptions.Abort:
            print("[yellow]Done[/yellow]")
            return

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
        self.detect_modes()
        print(f"[green]Game file is loaded: {os.path.basename(source)}[/green]")

    def _load(self, source: str) -> None:
        with open(source) as f:
            self._game = Game.from_json(f.read())

    async def run(self) -> None:
        while True:
            try:
                prompt = "Select mode:\n"
                for (key, mode) in self.modes.items():
                    prompt += f" {key}) {mode.name}\n"
                prompt += "> "
                choice_labels = list(self.modes.keys())
                choice = typer.prompt(prompt, type=click.Choice(choice_labels))
                method = self.modes[choice].method
                promise = method()
                if isinstance(promise, Coroutine):
                    await promise
            except click.exceptions.Abort:
                print("[yellow]Done[/yellow]")
                return
