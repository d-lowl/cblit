"""Phrasebook module."""
import dataclasses
from typing import Self

from dataclasses_json import DataClassJsonMixin

from cblit.gpt.gpt_api import DataClassGPTJsonMixin
from cblit.gpt.gpt_queries import GPTQuery
from cblit.session.country import ConstructedCountrySession

PHRASEBOOK_PROMPT = ""


@dataclasses.dataclass
class Phrase(DataClassGPTJsonMixin):
    """Phrase [DEPRECATED]."""
    original: str
    translation: str


@dataclasses.dataclass
class Phrasebook(DataClassJsonMixin):
    """Phrasebook."""
    phrases: list[Phrase]

    @staticmethod
    def compose_query(country: ConstructedCountrySession) -> str:
        """Deprecated.

        Args:
            country: Deprecated.

        Returns:
            str:
        """
        # TODO
        return GPTQuery().compose()

    @classmethod
    async def from_session(cls, session: ConstructedCountrySession) -> Self:
        """Deprecated.

        Args:
            session: Deprecated.

        Returns:
            Phrasebook: Deprecated.
        """
        # query = cls.compose_query(session.country)
        # response = await session.send(query, CRITICAL_PRIORITY)
        # phrases = Phrase.list_from_gpt_response(response)
        # phrases += [
        #     Phrase(original=session.country.example_sentence_translation,
        #     translation=session.country.example_sentence)
        # ]
        # TODO
        return cls([])
