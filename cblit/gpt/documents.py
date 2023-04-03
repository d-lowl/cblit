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

    @property
    def player_repr(self) -> str:
        raise NotImplementedError


QUENTA_PROMPT = "Generate me a quenta or a biography of a citizen of a neighbouring country."

@dataclasses.dataclass
class Quenta(DataClassGPTJsonMixin):
    name: str
    country: str
    dob: str
    employer: str
    employer_address: str
    job_title: str
    address: str

    @staticmethod
    def compose_query(country: ConstructedCountry) -> str:
        return GPTQuery().add(QUENTA_PROMPT).add_json([
            GPTJSONPart(question="Full name", key="name"),
            GPTJSONPart(question="Neighboring country name", key="country"),
            GPTJSONPart(question="Date of birth", key="dob"),
            GPTJSONPart(question="Employer company name", key="employer"),
            GPTJSONPart(question=f"Employer company address in {country.country_name}", key="employer_address"),
            GPTJSONPart(question="Job title of the person", key="job_title"),
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
    def from_quenta(cls, quenta: Quenta) -> Self:
        return cls(
            name=quenta.name,
            country=quenta.country,
            dob=quenta.dob
        )

    @property
    def game_repr(self) -> str:
        return f"Passport:\n" \
               f"--------\n" \
               f"Country of issue: {self.country}\n" \
               f"Country of birth: {self.country}\n" \
               f"Full name: {self.name}\n" \
               f"Date of birth: {self.dob}\n"

    @property
    def player_repr(self) -> str:
        return self.game_repr


@dataclasses.dataclass
class WorkPermit(Document):
    name: str
    employer: str
    employer_address: str
    job_title: str
    player_translation: str = ""

    @classmethod
    def from_quenta(cls, quenta: Quenta, session: ConstructedCountrySession) -> Self:
        self = cls(
            name=quenta.name,
            employer=quenta.employer,
            employer_address=quenta.employer_address,
            job_title=quenta.job_title
        )
        self.player_translation = session.from_english(self.game_repr)
        return self

    @property
    def player_repr(self) -> str:
        return self.player_translation

    @property
    def game_repr(self) -> str:
        return "Work Permit\n" \
               "--------\n" \
               f"Full Name: {self.name}\n" \
               f"Company of employment: {self.employer}\n" \
               f"Job title: {self.job_title}\n" \
               f"Company address: {self.employer_address}"
