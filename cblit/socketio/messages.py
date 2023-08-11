"""SocketIO messages."""
import dataclasses

from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class WaitPayload(DataClassJsonMixin):
    """Wait payload."""
    wait: bool


@dataclasses.dataclass
class SayPayload(DataClassJsonMixin):
    """Say payload."""
    who: str
    message: str
    difficulty: str


@dataclasses.dataclass
class GiveDocumentPayload(DataClassJsonMixin):
    """Give document payload."""
    index: int
    difficulty: str


@dataclasses.dataclass
class WinPayload(DataClassJsonMixin):
    """Win payload."""
    won: bool


@dataclasses.dataclass
class ErrorPayload(DataClassJsonMixin):
    """Error payload."""
    code: int
    message: str


@dataclasses.dataclass
class DocumentPayload(DataClassJsonMixin):
    """Document payload."""
    text: str


@dataclasses.dataclass
class DocumentsPayload(DataClassJsonMixin):
    """Documents payload."""
    documents: list[DocumentPayload]


@dataclasses.dataclass
class BriefPayload(DataClassJsonMixin):
    """Brief payload."""
    country_name: str
    language_name: str
    country_description: str
