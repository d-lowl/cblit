import dataclasses
from typing import List, Self

JSON_PROMPT = "I want every reply to be formatted as JSON. " \
              "Do not ever write anything other then valid JSON. Do not add \"Note\". " \
              "JSON multi-line strings should be put on a single line with new line characters, " \
              "as expected by JSON standard."

BREAK_PROMPT = ""


def enquote(query: str) -> str:
    return f"\"{query}\""


@dataclasses.dataclass
class GPTJSONPart:
    question: str
    key: str


@dataclasses.dataclass
class GPTQuery:
    parts: List[str] = dataclasses.field(default_factory=list)
    separator: str = "\n"

    def add(self, query: str) -> Self:
        self.parts += [query]
        return self

    def add_break(self) -> Self:
        return self.add(BREAK_PROMPT)

    def add_json(self, questions: List[GPTJSONPart]) -> Self:
        self.add(JSON_PROMPT)
        for question in questions:
            self.add(f"* {question.question}; key: {question.key}")
        return self

    def compose(self) -> str:
        return self.separator.join(self.parts)
