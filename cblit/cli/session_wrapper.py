import datetime
import glob
import os.path

from rich import print
import inspect
from typing import Callable, List, Optional, Type, Union

import click
import typer

from cblit.gpt.gpt_api import ChatSession


class SessionMethodWrapper:
    name: str
    method: Callable[[str], str]

    def __init__(self, name: str, method: Callable[[str], str]):
        self.name = name
        self.method = method

    def run(self) -> None:
        print(f"[green]{self.name}:[/green]")
        print("Ctrl-D or Ctrl-C to go back")
        while True:
            try:
                user_message = typer.prompt(">")
                gpt_response = self.method(user_message)
                print(f"<: {gpt_response}")
            except click.exceptions.Abort:
                print("[yellow]Done[/yellow]")
                return

    @staticmethod
    def is_compatible(signature: inspect.Signature) -> bool:
        parameters = signature.parameters
        return (
                len(parameters) == 1 and
                list(parameters.values())[0].annotation == str and
                signature.return_annotation == str
        )


LOG_DIRECTORY = os.path.join(os.getcwd(), os.pardir, "gpt-logs")


class SessionWrapper:
    session: Union[ChatSession, None] = None
    session_class: Type[ChatSession]
    methods: List[SessionMethodWrapper]

    def __init__(self, session_class: Type[ChatSession]):
        self.session_class = session_class
        self.methods = []

    def detect_methods(self) -> None:
        self.methods = [SessionMethodWrapper(name, method) for name, method in
                        inspect.getmembers(self.session, predicate=inspect.ismethod) if
                        not name.startswith("_") and SessionMethodWrapper.is_compatible(inspect.signature(method))]

    def select_mode(self) -> Optional[SessionMethodWrapper]:
        prompt_options = [f"{i + 1}) {method.name}" for i, method in enumerate(self.methods)]
        prompt_options += ["n) new", "l) load"]
        choice_labels = [str(i + 1) for i in range(len(self.methods))] + ["n", "l"]
        if self.session is not None:
            prompt_options += ["s) save", "p) print"]
            choice_labels += ["s", "p"]

        prompt = "; ".join(prompt_options)
        choices = click.Choice(choice_labels)
        choice = typer.prompt(prompt, type=choices)

        if choice == "n":
            self.generate()
            return None
        elif choice == "l":
            self.load()
            return None
        elif choice == "s":
            self.save()
            return None
        elif choice == "p":
            print(self.session)
            return None

        return self.methods[int(choice) - 1]

    def run(self) -> None:
        while True:
            try:
                method = self.select_mode()
                if method is not None:
                    method.run()
            except click.exceptions.Abort:
                print("[yellow]Done[/yellow]")
                return

    def generate(self) -> None:
        self.session = self.session_class.generate()
        self.detect_methods()
        print("[green]New session is generated[/green]")

    def save(self) -> None:
        filename = f"{self.session.__class__.__name__}-{datetime.datetime.now().isoformat()}.json"
        filename = typer.prompt("Enter filename to save the log file", default=filename)
        self._save(os.path.join(LOG_DIRECTORY, filename))
        print(f"[green]Session file is saved: {filename}[/green]")

    def _save(self, destination: str) -> None:
        if self.session is None:
            raise ValueError("Session has not been started, cannot save")
        # mypy does not recognise dataclass_json stuff
        session_json = self.session.to_json(indent=2)  # type: ignore
        with open(destination, "w") as f:
            f.write(session_json)

    def load(self) -> None:
        print("Select file to load:")
        paths = glob.glob(os.path.join(LOG_DIRECTORY, "*.json"))
        for i, path in enumerate(paths):
            print(f"  {i}) {os.path.basename(path)}")
        choice = typer.prompt("File index", type=click.Choice([str(i) for i in range(len(paths))]))
        source = paths[int(choice)]
        self._load(source)
        self.detect_methods()  # need to re-detect methods, as the current ones are bind to the previous session
        print(f"[green]Session file is loaded: {os.path.basename(source)}[/green]")

    def _load(self, source: str) -> None:
        with open(source, "r") as f:
            # mypy does not recognise dataclass_json stuff
            self.session = self.session_class.from_json(f.read())  # type: ignore
