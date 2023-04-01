import dataclasses
from typing import Self

from cblit.gpt.country import ConstructedCountrySession, ConstructedCountry
from cblit.gpt.gpt_api import DataClassGPTJsonMixin
from cblit.gpt.gpt_queries import GPTQuery, GPTJSONPart


@dataclasses.dataclass
class Document(DataClassGPTJsonMixin):
    @property
    def game_repr(self) -> str:
        raise NotImplementedError


QUENTA_PROMPT = "Generate me a quenta or a biography of a citizen of a neighbouring country."

@dataclasses.dataclass
class Quenta(DataClassGPTJsonMixin):
    name: str
    country: str
    dob: str
    employer: str
    employer_address: str
    address: str

    @staticmethod
    def compose_query(country: ConstructedCountry) -> str:
        return GPTQuery().add(QUENTA_PROMPT).add_json([
            GPTJSONPart(question="Full name", key="name"),
            GPTJSONPart(question="Neighboring country name", key="country"),
            GPTJSONPart(question="Date of birth", key="dob"),
            GPTJSONPart(question="Employer company name", key="employer"),
            GPTJSONPart(question=f"Employer company address in {country.country_name}", key="employer_address"),
            GPTJSONPart(question=f"Person's address in {country.country_name}", key="address"),
        ]).compose()

    @classmethod
    def from_session(cls, session: ConstructedCountrySession) -> Self:
        query = cls.compose_query(session.country)
        response = session.send(query)
        return cls.from_gpt_response(response)


@dataclasses.dataclass
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
