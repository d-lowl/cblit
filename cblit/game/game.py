"""Game session module."""
import dataclasses
from typing import Self, cast

from dataclasses_json import DataClassJsonMixin
from loguru import logger

from cblit.errors.errors import CblitArgumentError
from cblit.session.country import ConstructedCountrySession, Country
from cblit.session.immigrant.immigrant import Immigrant
from cblit.session.language.phrasebook import Phrasebook
from cblit.session.language.translator import ConlangEntry, TranslatorSession
from cblit.session.officer import LanguageUnderstanding, OfficerSession


@dataclasses.dataclass
class Game(DataClassJsonMixin):
    """Game session."""
    country_session: ConstructedCountrySession
    country: Country
    translator_session: TranslatorSession
    officer_session: OfficerSession
    immigrant: Immigrant
    phrasebook: Phrasebook
    started: bool
    won: bool

    @classmethod
    async def generate(cls) -> Self:
        """Generate game session.

        Returns:
            Game:
        """
        country_session = ConstructedCountrySession.instance()
        country = await country_session.new_country()
        translator_session = TranslatorSession(
            country.language_name,
            ConlangEntry(
                english=country.example_sentence_translation,
                conlang=country.example_sentence,
            ),
        )
        phrasebook = await Phrasebook.from_translator_session(translator_session)
        officer_session = OfficerSession()
        immigrant = await Immigrant.get_new(country, translator_session)
        return cls(
            country_session=country_session,
            country=country,
            translator_session=translator_session,
            officer_session=officer_session,
            immigrant=immigrant,
            phrasebook=phrasebook,
            started=False,
            won=False
        )

    async def start(self) -> str:
        """Start session, by saying initial phrase to the officer.

        Returns:
            str: initial reply from the officer
        """
        self.started = True
        reply = await self.officer_session.say("Hi!", LanguageUnderstanding.NATIVE_CLEAR)
        return cast(str, await self.translator_session.translate_to_conlang(reply))

    async def process_officer(self, reply: str) -> str:
        """Process officer's reply.

        Detect special sequences.
        * %%SUCCESS%% -- Winning condition met

        Args:
            reply (str): raw reply

        Returns:
            str: processed reply
        """
        if "%%SUCCESS%%" in reply:
            logger.debug("Winning condition met")
            self.won = True
        reply = reply.replace("%%SUCCESS%%", "")
        translation = cast(str, await self.translator_session.translate_to_conlang(reply))
        return translation

    async def say_to_officer(self, sentence: str) -> str:
        """Say a sentence to the officer.

        Args:
            sentence (str): sentence to say

        Returns:
            str: officer's reply
        """
        # is_english = await self.country_session.is_english(sentence, FORGET_PRIORITY)
        # is_national = await self.country_session.is_national(sentence, FORGET_PRIORITY)
        # if is_national:
        #     translation = await self.country_session.to_english(sentence, NORMAL_PRIORITY)
        #     reply = await self.officer_session.say(translation, LanguageUnderstanding.NATIVE_CLEAR)
        # elif is_english:
        #     reply = await self.officer_session.say(sentence, LanguageUnderstanding.NON_NATIVE)
        # else:
        #     reply = await self.officer_session.say(sentence, LanguageUnderstanding.NATIVE_GIBBERISH)
        translation = await self.translator_session.translate_from_conlang(sentence)
        reply = await self.officer_session.say(translation, LanguageUnderstanding.NATIVE_CLEAR)
        # TODO
        return await self.process_officer(reply)

    async def give_document(self, index: int) -> str:
        """Give a document to the officer.

        Args:
            index (int): document index

        Returns:
            str: officer's reply

        Raises:
            CblitArgumentError: Document with index does not exist
        """
        # raise NotImplementedError()
        if not (0 <= index < len(self.immigrant.documents)):
            raise CblitArgumentError(f"Document with {index} does not exist")
        reply = await self.officer_session.give_document(self.immigrant.documents[index])
        return await self.process_officer(reply)
