import dataclasses
from typing import Optional, Self

from cblit.gpt.gpt_api import ChatSession, Chat

OFFICER_PROMPT = "Pretend you are an immigration officer at an immigration office."
IMMIGRANT_PROMPT = "Pretend that I, a recent migrant, walk in, and approach your window."
REGISTRATION_PROCESS_PROMPT = "For an immigrant registration the procedure is as follows:"
REGISTRATION_STEPS_PROMPTS = [
    "Greeting and ask for what the purpose is. Confirm that this is for the registration.",
    "Ask for the name and identity documents",
    "If the identity documents are alright, scan them for filing",
    "Ask for a reason to immigrate",
    "If it is for work, ask for the work permit and employment contract",
    "Ask for the postal address",
    "Thank them and tell that they will receive; Say \"%SUCCESS%\" when finished"
]


def build_officer_prompt() -> str:
    registration_steps = "\n".join([f"{i+1}. {step}" for i, step in enumerate(REGISTRATION_STEPS_PROMPTS)])
    return "\n".join([
        OFFICER_PROMPT,
        IMMIGRANT_PROMPT,
        "",
        REGISTRATION_PROCESS_PROMPT,
        registration_steps
    ])


@dataclasses.dataclass
class OfficerSession(ChatSession):

    @classmethod
    def generate(cls) -> Self:
        chat = Chat.initialise_with_system(system_prompt=build_officer_prompt())
        return cls(chat=chat)

    def do_action(self, action: str) -> str:
        return ""

    def say(self, saying: str, is_local_language: bool, language_correctness: Optional[float]) -> str:
        return ""
