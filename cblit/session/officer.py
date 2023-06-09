"""Officer session module."""
import dataclasses
from enum import Enum
from typing import Self

from langchain import ConversationChain, PromptTemplate
from langchain.memory import ConversationBufferMemory

from cblit.cli.session_wrapper import wrap_session_method
from cblit.gpt.documents import Document
from cblit.llm.llm import get_llm
from cblit.session.session import BaseSession

OFFICER_PROMPT = (
    "Pretend you are an immigration officer at an immigration office. "
    "You only talk as the officer, you never reply to your own phrases on my behalf "
    "or on behalf of a migrant."
)
IMMIGRANT_PROMPT = "Pretend that I, a recent migrant, walk in, and approach your window."
REGISTRATION_PROCESS_PROMPT = "For an immigrant registration the procedure is as follows:"
REGISTRATION_STEPS_PROMPTS = [
    "Greeting and ask for what the purpose is. Confirm that this is for the registration.",
    "Ask for the name and identity documents",
    "If the identity documents are alright, scan them for filing",
    "Ask for a reason to immigrate",
    "If it is for work, ask for the work permit and employment contract",
    "Ask for the postal address",
    "Thank them and tell that they will receive the residence permit via post in 14 to 21 days",
    'Say "%%SUCCESS%%" when finished'
]
DIALOG_PROMPT = "This will be a dialog. Reply one phrase at a time please."


class OfficerPromptTemplate(PromptTemplate):
    """Langchain prompt template for the officer."""

    @staticmethod
    def get_template() -> str:
        """Get template string for the officer.

        Returns:
            str: template string
        """
        registration_steps = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(REGISTRATION_STEPS_PROMPTS)])
        return "\n".join([
            OFFICER_PROMPT,
            IMMIGRANT_PROMPT,
            "",
            REGISTRATION_PROCESS_PROMPT,
            registration_steps,
            DIALOG_PROMPT
        ])

    def __init__(self) -> None:
        """Initialise officer prompt template."""
        template = self.get_template() + """

Current conversation:
{history}
Visitor: {input}
Officer:
"""
        super().__init__(input_variables=["history", "input"], template=template)


class LanguageUnderstanding(Enum):
    """Enum for how well the officer understands lang."""
    NATIVE_CLEAR = 0
    NATIVE_GIBBERISH = 1
    NON_NATIVE = 2


@dataclasses.dataclass
class OfficerSession(BaseSession):
    """Officer session."""
    conversation: ConversationChain

    def __init__(self) -> None:
        """Initialise officer session."""
        self.conversation = ConversationChain(
            llm=get_llm(temperature=0),
            verbose=True,
            memory=ConversationBufferMemory(
                human_prefix="Visitor",
                ai_prefix="Officer"
            ),
            prompt=OfficerPromptTemplate(),
        )

    async def generate(self) -> Self:
        """Generate officer session.

        Nothing to explicitly generate.

        Returns:
            Self: officer session
        """
        return self

    @wrap_session_method()
    async def say(self, saying: str, language: LanguageUnderstanding) -> str:
        """Say to the officer.

        Args:
            saying (str): saying to pass to the officer
            language (LanguageUnderstanding): marker for the language understanding by the officer

        Returns:
            str: raw officer's response
        """
        understanding_prompt = ""
        if language == LanguageUnderstanding.NATIVE_CLEAR:
            understanding_prompt = "speaks clearly, you understand well"
        elif language == LanguageUnderstanding.NATIVE_GIBBERISH:
            understanding_prompt = "tries speaking in your native language, but fails"
        elif language == LanguageUnderstanding.NON_NATIVE:
            understanding_prompt = "speaks not in your native language, you understand about 5% of what is said"
        prompt = f"<{understanding_prompt}> {saying}"
        return await self.conversation.apredict(input=prompt)

    async def give_document(self, document: Document) -> str:
        """Give document to the officer.

        Args:
            document (Document): document to give

        Returns:
            str: officer's response
        """
        prompt = f"[I give the following document]\n{document.game_repr}"

        return await self.conversation.apredict(input=prompt)
