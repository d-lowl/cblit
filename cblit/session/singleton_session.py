"""Singleton Base Session module."""
import abc
from typing import Self

from cblit.session.session import BaseSession


class SingletonBaseSession(BaseSession, abc.ABC):
    """Singleton Base Session."""
    _instance: Self | None

    @classmethod
    def instance(cls) -> Self:
        """Get singleton instance."""
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = cls()
        return cls._instance
