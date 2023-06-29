"""Singleton Base Session module."""
import abc
from typing import Any, Self

from cblit.session.session import BaseSession


class SingletonBaseSession(BaseSession, abc.ABC):
    """Singleton Base Session."""
    _instance = None

    def __init__(self) -> None:
        """__init__ must not be called.

        Call instance() instead.
        """
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls, *args: Any, **kwargs: Any) -> Self:
        """Get singleton instance.

        Args:
            *args (Any): positional arguments
            **kwargs (Any): keyword arguments

        Returns:
            Self: singleton instance
        """
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._initialise(*args, **kwargs)
        return cls._instance

    def _initialise(self, *args: Any, **kwargs: Any) -> None:
        """Initialise singleton instance.

        Args:
            *args (Any): positional arguments
            **kwargs (Any): keyword arguments
        """
        raise NotImplementedError
