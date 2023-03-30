import dataclasses
from typing import Optional, Self

from cblit.gpt.gpt_api import ChatSession, Chat

OFFICER_PROMPT = ""


@dataclasses.dataclass
class Officer(ChatSession):

    @classmethod
    def generate(cls) -> Self:
        return cls()

    def __init__(self) -> None:
        super().__init__(Chat.initialise_with_system(OFFICER_PROMPT))

    def do_action(self, action: str) -> str:
        return ""

    def say(self, saying: str, is_local_language: bool, language_correctness: Optional[float]) -> str:
        return ""
