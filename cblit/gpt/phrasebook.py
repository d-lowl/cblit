import dataclasses
from typing import List, Self

from dataclasses_json import DataClassJsonMixin

from cblit.gpt.country import ConstructedCountrySession, ConstructedCountry
from cblit.gpt.gpt_api import DataClassGPTJsonMixin, CRITICAL_PRIORITY
from cblit.gpt.gpt_queries import GPTQuery, GPTJSONPart

PHRASEBOOK_PROMPT = ""


@dataclasses.dataclass
class Phrase(DataClassGPTJsonMixin):
    original: str
    translation: str


@dataclasses.dataclass
class Phrasebook(DataClassJsonMixin):
    phrases: List[Phrase]

    @staticmethod
    def compose_query(country: ConstructedCountry) -> str:
        return GPTQuery()\
            .add(f"Give me a phrasebook in {country.language_name}")\
            .add_json_list(
                [
                    GPTJSONPart("Original phrase in English", "original"),
                    GPTJSONPart(f"Translation to {country.language_name}", "translation")
                ]
            )\
            .add("In addition to whatever phrases you come up with, add these phrases, if they are not already there:")\
            .add("* What is your name?")\
            .add("* Passport")\
            .add("* Document")\
            .add("* Work")\
            .add("* Immigration office")\
            .add("* I want to register")\
            .add("* Required")\
            .add("* I do not understand")\
            .add("* Too fast")\
            .add("* Orchard")\
            .compose()

    @classmethod
    def from_session(cls, session: ConstructedCountrySession) -> Self:
        query = cls.compose_query(session.country)
        response = session.send(query, CRITICAL_PRIORITY)
        phrases = Phrase.list_from_gpt_response(response)
        phrases += [
            Phrase(original=session.country.example_sentence_translation, translation=session.country.example_sentence)
        ]
        return cls(phrases)
