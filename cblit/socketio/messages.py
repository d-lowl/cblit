import dataclasses
import json
from typing import Generic, TypeVar, TypeAlias, Union, Self, cast

from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class WaitPayload(DataClassJsonMixin):
    wait: bool


@dataclasses.dataclass
class SayPayload(DataClassJsonMixin):
    who: str
    message: str


@dataclasses.dataclass
class WinPayload(DataClassJsonMixin):
    won: bool


@dataclasses.dataclass
class ErrorPayload(DataClassJsonMixin):
    code: int
    message: str


IncomingMessagePayload: TypeAlias = Union[
    SayPayload
]

OutgoingMessagePayload: TypeAlias = Union[
    SayPayload,
    WaitPayload,
    ErrorPayload,
    WinPayload
]

T = TypeVar("T", bound=Union[IncomingMessagePayload, OutgoingMessagePayload])


@dataclasses.dataclass
class Message(Generic[T], DataClassJsonMixin):
    type: str
    payload: T

    def __init__(self, payload: T) -> None:
        self.type = payload.__class__.__name__
        self.payload = payload

    def serialize(self) -> str:
        return self.to_json()

    @classmethod
    def deserialize(cls, msg: str) -> Self:
        dumb = json.loads(msg)
        payload_type = dumb["type"]
        payload_cls: T = globals()[payload_type]
        return cls(cast(T, payload_cls.from_dict(dumb["payload"])))


IncomingMessage: TypeAlias = Message[IncomingMessagePayload]
OutgoingMessage: TypeAlias = Message[OutgoingMessagePayload]
