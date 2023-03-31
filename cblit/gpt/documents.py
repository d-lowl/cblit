import dataclasses
from typing import Self

from cblit.gpt.country import ConstructedCountrySession
from cblit.gpt.gpt_api import DataClassGPTJsonMixin


@dataclasses.dataclass
class Document(DataClassGPTJsonMixin):
    @property
    def game_repr(self) -> str:
        raise NotImplementedError


class Passport(Document):
    name: str
    country: str
    dob: str

    @classmethod
    def generate(cls, country_session: ConstructedCountrySession) -> Self:
        response = country_session.send(
            "Generate me a passport of a citizen of neighbouring country. "
            "I want every reply to be formated as JSON. Do not ever write anything other then valid JSON. "
            "Do not add \"Note\". "
            "* Full name; key: name * Country name; key: country * Date of birth: key: dob ")
        print(response)
        return cls.from_gpt_response(response)

    @property
    def game_repr(self) -> str:
        return f"Passport:" \
               f"Country of issue: {self.country}" \
               f"Country of birth: {self.country}" \
               f"Full name: {self.name}" \
               f"Date of birth: {self.dob}"
