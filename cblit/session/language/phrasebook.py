"""Phrasebook module."""
import dataclasses
from typing import Self

from dataclasses_json import DataClassJsonMixin

from cblit.session.language.translator import ConlangEntry, TranslatorSession

DEFAULT_PHRASEBOOK_PHRASES = [
    "Hello",
    "Goodbye",
    "Passport",
    "Documents",
    "Work",
    "Immigration office",
    "I want to register",
    "My address is ...",
    "Required",
    "I do not understand",
    "Too fast",
    "Help"
]


@dataclasses.dataclass
class Phrasebook(DataClassJsonMixin):
    """Phrasebook."""
    phrases: list[ConlangEntry]

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
