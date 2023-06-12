"""Quenta module."""

from langchain import LLMChain, PromptTemplate
from langchain.llms.base import BaseLLM
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from cblit.llm.llm import get_llm
from cblit.session.country import WRITER_PROMPT
from cblit.session.singleton_session import SingletonBaseSession


class Quenta(BaseModel):
    """Immigrant quenta model."""
    full_name: str = Field(description="Full name")
    country: str = Field(description="Country of nationality")
    dob: str = Field(description="Date of birth")
    employer: str = Field(description="Employer company name")
    employer_address: str = Field(description="Employer company address in the new country")
    job_title: str = Field(description="Job title of the person")
    job_duties: str = Field(description="Job duties")
    salary: int = Field(description="Salary per year in the new country currency")
    address: str = Field(description="Person's address in the new country")
    rent: int = Field(description="Rent price for the appartment per month")


class QuentaSession(SingletonBaseSession):
    """Quenta generation session."""
    template: str = "\n".join([
        WRITER_PROMPT,
        "{format_instructions}",
        (
            "Make up an immigrant-player quenta following the schema above, "
            "for an immigrant who has just moved from {from_country} to {to_country}."
        )
    ])
    llm: BaseLLM
    quenta_parser: PydanticOutputParser[Quenta]
    prompt: PromptTemplate
    chain: LLMChain

    def _initialise(self) -> None:
        """Initialise quenta generation session."""
        self.llm = get_llm(temperature=0.7)
        self.quenta_parser = PydanticOutputParser(pydantic_object=Quenta)
        self.prompt = PromptTemplate(
            template=self.template,
            input_variables=["from_country", "to_country"],
            partial_variables={"format_instructions": self.quenta_parser.get_format_instructions()}
        )
        self.quenta_chain = LLMChain(
            llm=self.llm,
            verbose=True,
            prompt=self.prompt
        )

    async def new_quenta(self, from_country: str, to_country: str) -> Quenta:
        """Generate new quenta for a country.

        Args:
            from_country (str): country moved from
            to_country (str): country moved to

        Returns:
            Quenta: generated quenta
        """
        return self.quenta_parser.parse(await self.quenta_chain.arun(from_country=from_country, to_country=to_country))
