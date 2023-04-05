import dataclasses
from typing import Tuple
from loguru import logger

from dataclasses_json import dataclass_json

from typing_extensions import Self

from cblit.gpt.gpt_api import ChatSession, Chat, DataClassGPTJsonMixin
from cblit.gpt.gpt_queries import JSON_PROMPT, GPTQuery, enquote, GPTJSONPart

WRITER_PROMPT = "You are a young sci-fi writer. You need to write creative things. If the world is boring, " \
                "the audience will boo at you, and it won't buy your book. Every time you give an answer re-evaluate " \
                "if it is boring or not. If you think it's boring, try writing again. Try to impress the readers. " \
                "What you come up with must not be similar to English."

COUNTRY_PROMPT = "Construct a country. Give short answers to the following questions:\n" \
                 "* Country name, key: country_name\n" \
                 "* Country short description, key: country_description\n" \
                 "* Country people short description, key: people_description\n" \
                 "* National language name, key: language_name\n" \
                 "* National language short description, key: language_description\n" \
                 "* Example sentence in the national language, key: example_sentence\n" \
                 "* Its translation to English, key: example_sentence_translation\n"

TRANSLATION_PROMPT = "Translate from {} to {}:"


def format_translation_prompt(source_language: str, target_language: str, prompt: str) -> str:
    translation_prompt = TRANSLATION_PROMPT.format(source_language, target_language)
    return GPTQuery().add(translation_prompt).add(enquote(prompt)).add_json([
        GPTJSONPart("Translation", "translation")
    ]).compose()


@dataclasses.dataclass
class ConstructedCountry(DataClassGPTJsonMixin):
    country_name: str
    country_description: str
    people_description: str
    language_name: str
    language_description: str
    example_sentence: str
    example_sentence_translation: str

    @staticmethod
    def line_to_pair(line: str) -> Tuple[str, str]:
        sections = [x.strip() for x in line.split(":")]
        if len(sections) != 2:
            raise ValueError(f"Expected a question and an answer only, but got: {line}")

        return sections[0], sections[1]


@dataclasses.dataclass
class Translation(DataClassGPTJsonMixin):
    translation: str


@dataclass_json
@dataclasses.dataclass
class ConstructedCountrySession(ChatSession):
    country: ConstructedCountry

    @staticmethod
    def _parse_translation(response: str) -> str:
        sections = response.split(":")
        if sections[0] != "Translation":
            raise ValueError(f"Expected Translation, got {sections}")

        return ":".join(sections[1:]).strip()

    @classmethod
    def generate(cls) -> Self:
        chat = Chat.initialise_with_system(system_prompt=("\n".join([WRITER_PROMPT, JSON_PROMPT])))
        session = ChatSession(chat=chat)
        country_response = session.send(COUNTRY_PROMPT)
        country = ConstructedCountry.from_gpt_response(country_response)
        return cls(
            chat=session.chat,
            country=country
        )

    def _translate(self, from_lang: str, to_lang: str, sentence: str) -> str:
        prompt = format_translation_prompt(from_lang, to_lang, sentence)
        logger.debug(f"Translation prompt: '{prompt}'")
        response = self.send(prompt)
        logger.debug(f"Translation response: '{response}'")
        translation = Translation.from_gpt_response(response)
        logger.debug(f"Translation: '{translation}'")
        return translation.translation

    def from_english(self, sentence: str) -> str:
        return self._translate("English", self.country.language_name, sentence)

    def to_english(self, sentence: str) -> str:
        return self._translate(self.country.language_name, "English", sentence)
