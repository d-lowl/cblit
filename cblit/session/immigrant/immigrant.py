"""Immigrant module."""
import asyncio
import dataclasses
from typing import Self

from dataclasses_json import DataClassJsonMixin

from cblit.session.country import Country
from cblit.session.immigrant.document import Document, EmploymentAgreement, Passport, TenancyAgreement, WorkPermit
from cblit.session.immigrant.quenta import Quenta, QuentaSession
from cblit.session.language.translator import TranslatorSession


@dataclasses.dataclass
class Immigrant(DataClassJsonMixin):
    """Immigrant in-game profile."""
    quenta: Quenta
    documents: list[Document]

    @classmethod
    async def get_new(cls, country: Country, translator: TranslatorSession) -> Self:
        """Generate new immigrant player.

        Args:
            country (Country): constructed country to use
            translator (TranslatorSession): translator to translate from English to Conlang

        Returns:
             Immigrant: immigrant-player instance
        """
        quenta = await QuentaSession.instance().new_quenta(country.neighbour_country_name, country.country_name)
        documents = list(await asyncio.gather(
            Passport.from_quenta(quenta),
            WorkPermit.from_quenta(quenta, translator),
            EmploymentAgreement.from_quenta(quenta, translator),
            TenancyAgreement.from_quenta(quenta, translator),
        ))
        return cls(
            quenta=quenta,
            documents=documents,
        )
