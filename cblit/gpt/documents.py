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
    job_duties: str
    salary: str
    address: str
    rent: str

    @staticmethod
    def compose_query(country: ConstructedCountry) -> str:
        return GPTQuery().add(QUENTA_PROMPT).add_json([
            GPTJSONPart(question="Full name", key="name"),
            GPTJSONPart(question="Neighboring country name", key="country"),
            GPTJSONPart(question="Date of birth", key="dob"),
            GPTJSONPart(question="Employer company name", key="employer"),
            GPTJSONPart(question=f"Employer company address in {country.country_name}", key="employer_address"),
            GPTJSONPart(question="Job title of the person", key="job_title"),
            GPTJSONPart(question="Job duties", key="job_duties"),
            GPTJSONPart(question="Salary", key="salary"),
            GPTJSONPart(question=f"Person's address in {country.country_name}", key="address"),
            GPTJSONPart(question="Rent price for that apartment", key="rent"),
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


@dataclasses.dataclass
class EmploymentAgreement(Document):
    employee_name: str
    employer: str
    employer_address: str
    job_title: str
    job_duties: str
    salary: str
    player_translation: str = ""

    @classmethod
    def from_quenta(cls, quenta: Quenta, session: ConstructedCountrySession) -> Self:
        self = cls(
            employee_name=quenta.name,
            employer=quenta.employer,
            employer_address=quenta.employer_address,
            job_title=quenta.job_title,
            job_duties=quenta.job_duties,
            salary=quenta.salary
        )
        self.player_translation = session.from_english(self.game_repr)
        return self

    @property
    def player_repr(self) -> str:
        return self.player_translation

    @property
    def game_repr(self) -> str:
        return "Employment Agreement: \n" \
               "--------\n" \
               f"Employee Name: {self.employee_name}\n" \
               f"Employer Name: {self.employer}\n" \
               f"Job title: {self.job_title}\n" \
               f"Job duties: {self.job_duties}\n" \
               f"Salary: {self.salary}\n" \
               f"Company address: {self.employer_address}"


@dataclasses.dataclass
class TenancyAgreement(Document):
    name: str
    address: str
    rent: str
    player_translation: str = ""

    @classmethod
    def from_quenta(cls, quenta: Quenta, session: ConstructedCountrySession) -> Self:
        self = cls(
            name=quenta.name,
            address=quenta.address,
            rent=quenta.rent
        )
        self.player_translation = session.from_english(self.game_repr)
        return self

    @property
    def player_repr(self) -> str:
        return self.player_translation

    @property
    def game_repr(self) -> str:
        return "Tenancy Agreement\n" \
               "--------\n" \
               f"Full Name: {self.name}\n" \
               f"Address: {self.address}\n" \
               f"Rent price: {self.rent}\n"
