import dataclasses
from typing import Tuple

from dataclasses_json import dataclass_json
from rich import print

from typing_extensions import Self

from cblit.gpt.gpt_api import ChatSession, Chat

WRITER_PROMPT = "You are a young sci-fi writer. You need to write creative things. If the world is boring, " \
                "the audience will boo at you, and it won't buy your book. Every time you give an answer re-evaluate " \
                "if it is boring or not. If you think it's boring, try writing again. Try to impress the readers. " \
                "What you come up with must not be similar to English"

COUNTRY_PROMPT = "Construct a country. Give short answers to the following questions:\n" \
                 "* Country name\n" \
                 "* Country short description\n" \
                 "* Country people short description\n" \
                 "* National language name\n" \
                 "* National language short description\n" \
                 "* Example sentence in the national language\n" \
                 "* Its translation to English\n"

TRANSLATION_PROMPT = "Translate from {} to {}: {}. Give your answer in this format \"Translation: " \
                     "X\". Avoid providing unnecessary details. If you think there\'s no translation, respond with: " \
                     "\"Translation: []\""


def format_translation_prompt(source_language: str, target_language: str, prompt: str) -> str:
    return TRANSLATION_PROMPT.format(source_language, target_language, prompt)


@dataclass_json
@dataclasses.dataclass
class ConstructedCountry:
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

    @classmethod
    def from_gpt_response(cls, response: str) -> Self:
        lines = [x.replace("\n", "") for x in response.split("\n\n") if x.strip() != ""]
        if len(lines) != 7:
            raise ValueError(f"Expected 7 questions answered, but got {len(lines)}: {response}; {lines}")

        pairs = [ConstructedCountry.line_to_pair(line) for line in lines]

        # TODO improve customisability
        if pairs[0][0] == "Country name":
            country_name = pairs[0][1]
        else:
            raise ValueError(f"Expected Country name, but got {pairs[0]}")

        if pairs[1][0] == "Country short description":
            country_description = pairs[1][1]
        else:
            raise ValueError(f"Expected Country short description, but got {pairs[1]}")

        if pairs[2][0] == "Country people short description":
            people_description = pairs[2][1]
        else:
            raise ValueError(f"Expected Country people short description, but got {pairs[2]}")

        if pairs[3][0] == "National language name":
            language_name = pairs[3][1]
        else:
            raise ValueError(f"Expected National language name, but got {pairs[3]}")

        if pairs[4][0] == "National language short description":
            language_description = pairs[4][1]
        else:
            raise ValueError(f"National language short description, but got {pairs[4]}")

        if pairs[5][0] == "Example sentence in the national language":
            example_sentence = pairs[5][1]
        else:
            raise ValueError(f"Expected Example sentence in the national language, but got {pairs[5]}")

        if pairs[6][0] == "Its translation to English":
            example_sentence_translation = pairs[6][1]
        else:
            raise ValueError(f"Expected Its translation to English, but got {pairs[6]}")

        return ConstructedCountry(
            country_name=country_name,
            country_description=country_description,
            people_description=people_description,
            language_name=language_name,
            language_description=language_description,
            example_sentence=example_sentence,
            example_sentence_translation=example_sentence_translation
        )


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
    def generate(cls):
        chat = Chat.initialise_with_system(system_prompt=WRITER_PROMPT)
        session = ChatSession(chat=chat)
        country_response = session.send(COUNTRY_PROMPT)
        country = ConstructedCountry.from_gpt_response(country_response)
        return ConstructedCountrySession(
            chat=session.chat,
            country=country
        )

    def from_english(self, sentence: str) -> str:
        prompt = format_translation_prompt("English", self.country.language_name, sentence)
        print(prompt)
        response = self.send(prompt)
        return ConstructedCountrySession._parse_translation(response)

    def to_english(self, sentence: str) -> str:
        prompt = format_translation_prompt(self.country.language_name, "English", sentence)
        response = self.send(prompt)
        return ConstructedCountrySession._parse_translation(response)
