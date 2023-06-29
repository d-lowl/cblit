"""Wrap Langchain powered LLM session."""
import inspect
import os.path
from collections.abc import Callable, Coroutine
from enum import Enum
from types import MappingProxyType
from typing import Any, Self, TypeAlias, cast

import click
import typer
from rich import print

from cblit.session.session import BaseSession

SessionMethod: TypeAlias = Callable[..., Any] | Callable[..., Coroutine[Any, Any, Any]]


def wrap_session_method() -> Callable[..., Any]:
    """Mark method for session wrapping.

    Returns:
        Callable[..., Any]: a method marked for wrapping
    """
    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        func.is_session_method = True  # type: ignore[attr-defined]
        return func
    return wrapper


def prompt_enum(param_name: str, enum: type[Enum]) -> Enum:
    """Prompt for an enum parameter.

    Args:
        param_name (str): parameter name
        enum (Type[Enum]): enum subtype to prompt for

    Returns:
        Enum: a resulting enum element
    """
    enum_elements = list(enum.__members__.values())
    elements_dict = {element.value: element for element in enum_elements}
    prompt_str = f"{param_name}: " + ", ".join([f"{value}) {element.name}" for value, element in elements_dict.items()])
    choices = click.Choice([str(value) for value in elements_dict])
    choice = typer.prompt(prompt_str, type=choices)
    return elements_dict[int(choice)]


def prompt_str(param_name: str) -> str:
    """Prompt for a str parameter.

    Args:
        param_name (str): parameter name

    Returns:
        str: parameter value to pass
    """
    return cast(str, typer.prompt(f"{param_name}"))


def prompt_parameter(param: inspect.Parameter) -> Any:
    """Prompt for a single parameter based on its type.

    Args:
        param (inspect.Parameter): parameter to prompt for

    Returns:
        Any: parameter value to pass
    """
    if param.annotation in [str, inspect.Parameter.empty]:
        return prompt_str(param.name)
    elif issubclass(param.annotation, Enum):
        return prompt_enum(param.name, param.annotation)


class SessionMethodWrapper:
    """Session Method Wrapper."""
    name: str
    method: SessionMethod
    parameters: MappingProxyType[str, inspect.Parameter]

    def __init__(self, name: str, method: Callable[..., Any]) -> None:
        """Wrap a method.

        Args:
            name (str): method name for displaying
            method (Callable[..., Any]): method to call
        """
        self.name = name
        self.method = method
        self.parameters = inspect.signature(method).parameters

    def _build_args(self) -> dict[str, Any]:
        """Prompt for all arguments required by the function.

        Returns:
            Dict[str, Any]: arguments
        """
        return {name: prompt_parameter(param) for name, param in self.parameters.items()}

    async def _call_method(self) -> None:
        """Call the wrapped method."""
        arguments = self._build_args()
        result = await self.method(**arguments)
        print("<: "+str(result))

    async def run(self) -> None:
        """Run wrapped method continuously."""
        print(f"[green]::{self.name}::[/green]")
        print("Ctrl-D or Ctrl-C to go back")
        while True:
            try:
                await self._call_method()
            except click.exceptions.Abort:
                print("[yellow]Done[/yellow]")
                return

    @staticmethod
    def is_compatible(func: Callable[..., Any]) -> bool:
        """Check whether the function is compatible with the wrapper.

        Args:
            func (Callable): function to check

        Returns:
            bool: check results
        """
        return hasattr(func, "is_session_method") and func.is_session_method


LOG_DIRECTORY = os.path.join(os.getcwd(), os.pardir, "gpt-logs")


class SessionWrapper:
    """Session Wrapper."""
    session: BaseSession | None = None
    methods: list[SessionMethodWrapper]

    def __init__(self, session: BaseSession):
        """Wrap session as CLI.

        Args:
            session (BaseSession): session to wrap
        """
        self.session = session
        self.methods = []

    def detect_methods(self) -> None:
        """Detect method of the session to wrap."""
        self.methods = [SessionMethodWrapper(name, method) for name, method in
                        inspect.getmembers(self.session, predicate=inspect.ismethod) if
                        SessionMethodWrapper.is_compatible(method)]

    async def select_mode(self) -> SessionMethodWrapper:
        """Select method to run."""
        prompt_options = [f"{i + 1}) {method.name}" for i, method in enumerate(self.methods)]
        choice_labels = [str(i + 1) for i in range(len(self.methods))]

        prompt = "; ".join(prompt_options)
        choices = click.Choice(choice_labels)
        choice = typer.prompt(prompt, type=choices)

        return self.methods[int(choice) - 1]

    async def run(self) -> None:
        """Run session wrapper."""
        while True:
            try:
                method = await self.select_mode()
                await method.run()
            except click.exceptions.Abort:
                print("[yellow]Done[/yellow]")
                return

    @classmethod
    def from_session(cls, session: BaseSession) -> Self:
        """Construct wrapper from existing session."""
        wrapper = cls(session)
        wrapper.detect_methods()
        return wrapper
