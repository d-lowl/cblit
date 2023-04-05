import dataclasses
from typing import List, Self

from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class CompletionMessage:
    content: str
    role: str


@dataclasses.dataclass
class CompletionChoice:
    finish_reason: str
    index: int
    message: CompletionMessage


@dataclasses.dataclass
class CompletionUsage(DataClassJsonMixin):
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: Self) -> None:
        self.completion_tokens += other.completion_tokens
        self.prompt_tokens += other.prompt_tokens
        self.total_tokens += other.total_tokens


@dataclasses.dataclass
class Completion:
    choices: List[CompletionChoice]
    created: int
    id: str
    model: str
    object: str
    usage: CompletionUsage
