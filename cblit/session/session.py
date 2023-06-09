"""Langchain powered LLM session base."""
from typing import Self


class BaseSession:
    """Base LLM session."""
    async def generate(self) -> Self:
        """Generate session.

        Not implemented method, MUST be defined

        Raises:
            NotImplementedError: always
        """
        raise NotImplementedError
