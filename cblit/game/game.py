import dataclasses
from typing import List, Self

from dataclasses_json import DataClassJsonMixin

from cblit.gpt.country import ConstructedCountrySession
from cblit.gpt.documents import Quenta, Document, Passport, WorkPermit, EmploymentAgreement, TenancyAgreement
from cblit.gpt.officer import OfficerSession
from cblit.gpt.phrasebook import Phrasebook


@dataclasses.dataclass
class Game(DataClassJsonMixin):
    country_session: ConstructedCountrySession
    officer_session: OfficerSession
    quenta: Quenta
    documents: List[Document]
    phrasebook: Phrasebook

    @classmethod
    def generate(cls) -> Self:
        country_session = ConstructedCountrySession.generate()
        phrasebook = Phrasebook.from_session(country_session)
        officer_session = OfficerSession.generate()
        quenta = Quenta.from_session(country_session)
        documents = cls.generate_documents(quenta, country_session)
        return cls(
            country_session=country_session,
            officer_session=officer_session,
            quenta=quenta,
            documents=documents,
            phrasebook=phrasebook
        )

    @staticmethod
    def generate_documents(quenta: Quenta, session: ConstructedCountrySession) -> List[Document]:
        return [
            Passport.from_quenta(quenta),
            WorkPermit.from_quenta(quenta, session),
            EmploymentAgreement.from_quenta(quenta, session),
            TenancyAgreement.from_quenta(quenta, session)
        ]