import dataclasses
from typing import List, Self

from dataclasses_json import DataClassJsonMixin

from cblit.gpt.country import ConstructedCountrySession, ConstructedCountry
from cblit.gpt.gpt_api import DataClassGPTJsonMixin
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
            .add("* Document")\
            .add("* Work")\
            .add("* Immigration office")\
            .add("* Required")\
            .add("* I do not understand")\
            .add("* Too fast")\
            .add("* Orchard")\
            .compose()

    @classmethod
    def from_session(cls, session: ConstructedCountrySession) -> Self:
        query = cls.compose_query(session.country)
        response = session.send(query)
        return cls(Phrase.list_from_gpt_response(response))
