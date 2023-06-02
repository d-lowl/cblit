import dataclasses
from enum import Enum

from langchain import PromptTemplate, OpenAI, ConversationChain
from langchain.memory import ConversationBufferMemory

from cblit.gpt.documents import Document

OFFICER_PROMPT = "Pretend you are an immigration officer at an immigration office. " \
                 "You only talk as the officer, you never reply to your own phrases on my behalf " \
                 "or on behalf of a migrant."
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
    "Say \"%%SUCCESS%%\" when finished"
]
DIALOG_PROMPT = "This will be a dialog. Reply one phrase at a time please."


def build_officer_prompt() -> str:
    registration_steps = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(REGISTRATION_STEPS_PROMPTS)])
    return "\n".join([
        OFFICER_PROMPT,
        IMMIGRANT_PROMPT,
        "",
        REGISTRATION_PROCESS_PROMPT,
        registration_steps,
        DIALOG_PROMPT
    ])


def build_officer_langchain_prompt() -> PromptTemplate:
    template = build_officer_prompt() + """

    Current conversation:
    {history}
    Visitor: {input}
    Officer:
    """
    return PromptTemplate(input_variables=["history", "input"], template=template)


class LanguageUnderstanding(Enum):
    NATIVE_CLEAR = 0
    NATIVE_GIBBERISH = 1
    NON_NATIVE = 2


@dataclasses.dataclass
class OfficerLangchain:
    conversation: ConversationChain

    def __init__(self) -> None:
        llm = OpenAI(temperature=0)  # type: ignore [call-arg]
        prompt = build_officer_langchain_prompt()
        self.conversation = ConversationChain(
            llm=llm,
            verbose=True,
            memory=ConversationBufferMemory(
                human_prefix="Visitor",
                ai_prefix="Officer"
            ),
            prompt=prompt,
        )

    async def say(self, saying: str, language: LanguageUnderstanding) -> str:
        understanding_prompt = ""
        if language == LanguageUnderstanding.NATIVE_CLEAR:
            understanding_prompt = "speaks clearly, you understand well"
        elif language == LanguageUnderstanding.NATIVE_GIBBERISH:
            understanding_prompt = "tries speaking in your native language, but fails"
        elif language == LanguageUnderstanding.NON_NATIVE:
            understanding_prompt = "speaks not in your native language, you understand about 75% of what is said"
        prompt = f"<{understanding_prompt}> {saying}"
        return await self.conversation.apredict(input=prompt)

    async def give_document(self, document: Document) -> str:
        prompt = f"[I give the following document]\n{document.game_repr}"

        return await self.conversation.apredict(input=prompt)
