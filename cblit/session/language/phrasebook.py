"""Phrasebook module."""
from typing import Self

from pydantic import BaseModel, Field

from cblit.session.language.translator import ConlangEntry, TranslatorSession

DEFAULT_PHRASEBOOK_PHRASES = [
    "Hello",
    "Goodbye",
    "Passport",
    "Identity documents",
    "My name is ...",
    "How are you?",
    "I am good, thank you!",
    "My reason to enter is work/study/tourism",
    "Immigration office",
    "I want to register",
    "My address is ...",
    "I do not understand",
    "What is ...?",
    "Help"
]


class Phrasebook(BaseModel):
    """Phrasebook."""
    phrases: list[ConlangEntry] = Field(description="A list of conlang entries")

    @classmethod
    async def from_translator_session(
            cls,
            translator_session: TranslatorSession,
            phrases_to_translate: list[str] | None = None
    ) -> Self:
        """Generate a phrasebook from translator session.

        Args:
            translator_session (TranslatorSession): session for word translation
            phrases_to_translate (Optional[list[str]]): optional phrases list, has a default

        Returns:
            Phrasebook: for a conlang
        """
        if phrases_to_translate is None:
            phrases_to_translate = DEFAULT_PHRASEBOOK_PHRASES

        phrases = [await translator_session.translate("English", translator_session.conlang_name, phrase)
                   for phrase in phrases_to_translate]
        print(phrases)
        return cls(phrases=phrases)
