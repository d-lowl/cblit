"""Country module."""

from langchain import LLMChain, PromptTemplate
from langchain.chains.base import Chain
from langchain.llms.base import BaseLLM
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import OutputParserException
from pydantic import BaseModel, Field
from retry import retry

from cblit.llm.llm import get_llm
from cblit.session.singleton_session import SingletonBaseSession

WRITER_PROMPT = (
    "You are a young sci-fi writer. You need to write creative things. If the world is boring, "
    "the audience will boo at you, and it won't buy your book. Every time you give an answer re-evaluate "
    "if it is boring or not. If you think it's boring, try writing again. Try to impress the readers. "
    "What you come up with must not be similar to English."
)


class Country(BaseModel):
    """Model for country generation."""
    country_name: str = Field(description="The name of the country")
    country_description: str = Field(description="A short description of the country")
    country_currency_name: str = Field(description="Currency used in the country")
    neighbour_country_name: str = Field(description="The name of another country that neighbours this")
    people_description: str = Field(description="A short description of people living in the country")
    language_name: str = Field(description="A national language name")
    language_description: str = Field(description="A short description of the language")
    example_sentence: str = Field(description="An example sentence in this language")
    example_sentence_translation: str = Field(description="Translation of this sentence to English")


def get_country_prompt_template(parser: PydanticOutputParser[Country]) -> PromptTemplate:
    """Build a country langchain prompt.

    Args:
        parser (PydanticOutputParser): parser for the generated country

    Returns:
        PromptTemplate: resulting prompt template
    """
    template = "\n".join([
        WRITER_PROMPT,
        "{format_instructions}",
        "{dummy} Make up a constructed non-existing country on another planet, where they speak a non-English language",
    ])
    return PromptTemplate(
        template=template,
        input_variables=["dummy"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )


class ConstructedCountrySession(SingletonBaseSession):
    """Constructed country session."""
    llm: BaseLLM
    country_parser: PydanticOutputParser[Country]
    country_chain: Chain

    def _initialise(self) -> None:
        """Initialise country generation session."""
        self.llm = get_llm(temperature=0.7)
        self.country_parser = PydanticOutputParser(pydantic_object=Country)
        prompt = get_country_prompt_template(self.country_parser)
        self.country_chain = LLMChain(
            llm=self.llm,
            verbose=True,
            prompt=prompt,
        )

    @retry(exceptions=OutputParserException, tries=5)
    async def new_country(self) -> Country:
        """Get new country.

        Returns:
            Country: a constructed country
        """
        return self.country_parser.parse(await self.country_chain.arun(dummy=""))
