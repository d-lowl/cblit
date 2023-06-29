"""Document module."""
import asyncio
import dataclasses
from typing import Self

from cblit.session.immigrant.quenta import Quenta
from cblit.session.language.translator import TranslatorSession


@dataclasses.dataclass
class Document:
    """Base document class."""
    # officer representation of the document, i.e. in English
    officer_representation: str
    # player representation of the document, i.e. in Conlang if appropriate
    player_representation: str

    @classmethod
    async def from_list(cls, name: str, lines: list[str], translator: TranslatorSession | None = None) -> Self:
        """Build a document from a list of document lines.

        Args:
            name (str): document name
            lines (list[str]): a list of document entries/lines
            translator (Optional[TranslatorSession]): a translator session, if set, the document will be translated

        Returns:
            Self: complete document
        """
        def get_representation(_name: str, _lines: list[str]) -> str:
            """Build representation of the document.

            Args:
                _name (str): document name
                _lines (str): a list of document entries/lines

            Returns:
                str: document representation
            """
            return "\n".join(
                [_name, len(_name)*"="] + _lines
            )

        officer_representation = get_representation(name, lines)
        if translator is not None:
            translated_name = await translator.translate_to_conlang(name)
            translated_lines = list(await asyncio.gather(*[translator.translate_to_conlang(line) for line in lines]))
            player_representation = get_representation(translated_name, translated_lines)
        else:
            player_representation = officer_representation

        return cls(officer_representation=officer_representation, player_representation=player_representation)


class Passport(Document):
    """Passport."""
    @classmethod
    async def from_quenta(cls, quenta: Quenta) -> Self:
        """Generate a passport from quenta object.

        Args:
            quenta (Quenta): quenta

        Returns:
             Document: passport
        """
        return await cls.from_list(
            name="Passport",
            lines=[
                f"Country of issue: {quenta.country}",
                f"Country of birth: {quenta.country}",
                f"Full name: {quenta.full_name}",
                f"Date of birth: {quenta.dob}"
            ],
            translator=None
        )


class WorkPermit(Document):
    """Work Permit."""
    @classmethod
    async def from_quenta(cls, quenta: Quenta, translator: TranslatorSession) -> Self:
        """Generate a work permit from quenta object.

        Args:
            quenta (Quenta): quenta
            translator (TranslatorSession): translator

        Returns:
             Document: work permit
        """
        return await cls.from_list(
            name="Work Permit",
            lines=[
                f"Full Name: {quenta.full_name}",
                f"Company of employment: {quenta.employer}",
                f"Job title: {quenta.job_title}",
                f"Job description: {quenta.job_duties}",
                f"Company address: {quenta.employer_address}"
            ],
            translator=translator
        )


class EmploymentAgreement(Document):
    """Employment Agreement."""
    @classmethod
    async def from_quenta(cls, quenta: Quenta, translator: TranslatorSession) -> Self:
        """Generate a employment agreement from quenta object.

        Args:
            quenta (Quenta): quenta
            translator (TranslatorSession): translator

        Returns:
             Document: employment agreement
        """
        return await cls.from_list(
            name="Employment Agreement",
            lines=[
                f"Employee Name: {quenta.full_name}",
                f"Employer Name: {quenta.employer}",
                f"Job title: {quenta.job_title}",
                f"Job duties: {quenta.job_duties}",
                f"Salary: {quenta.salary}",
                f"Company address: {quenta.employer_address}"
            ],
            translator=translator
        )


class TenancyAgreement(Document):
    """Tenancy Agreement."""
    @classmethod
    async def from_quenta(cls, quenta: Quenta, translator: TranslatorSession) -> Self:
        """Generate a tenancy agreement from quenta object.

        Args:
            quenta (Quenta): quenta
            translator (TranslatorSession): translator

        Returns:
             Document: tenancy agreement
        """
        return await cls.from_list(
            name="Tenancy Agreement",
            lines=[
                f"Full Name: {quenta.full_name}\n",
                f"Address: {quenta.address}\n",
                f"Rent price: {quenta.rent}\n"
            ],
            translator=translator
        )
