from rich import print
import inspect
from typing import Callable, List

import click
import typer

from cblit.gpt.gpt_api import ChatSession


class SessionMethodWrapper:
    name: str
    method: Callable[[str], str]

    def __init__(self, name: str, method: Callable[[str], str]):
        self.name = name
        self.method = method

    def run(self):
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


class SessionWrapper:
    methods: List[SessionMethodWrapper]

    def __init__(self, session: ChatSession):
        self.methods = [SessionMethodWrapper(name, method) for name, method in
                        inspect.getmembers(session, predicate=inspect.ismethod) if
                        not name.startswith("_") and SessionMethodWrapper.is_compatible(inspect.signature(method))]

    def select_mode(self) -> SessionMethodWrapper:
        prompt_options = [f"{i + 1}) {method.name}" for i, method in enumerate(self.methods)]
        prompt = "; ".join(prompt_options)
        choices = click.Choice([str(i + 1) for i in range(len(self.methods))])
        choice = typer.prompt(prompt, type=choices)
        return self.methods[int(choice) - 1]

    def run(self):
        while True:
            method = self.select_mode()
            method.run()
