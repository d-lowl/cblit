import dataclasses
from typing import List, Self

from dataclasses_json import DataClassJsonMixin
from loguru import logger

from cblit.gpt.country import ConstructedCountrySession
from cblit.gpt.documents import Quenta, Document, Passport, WorkPermit, EmploymentAgreement, TenancyAgreement
from cblit.gpt.gpt_api import ChatRole, NORMAL_PRIORITY, FORGET_PRIORITY
from cblit.gpt.officer import OfficerSession, LanguageUnderstanding
from cblit.gpt.phrasebook import Phrasebook


@dataclasses.dataclass
class Game(DataClassJsonMixin):
    country_session: ConstructedCountrySession
    officer_session: OfficerSession
    quenta: Quenta
    documents: List[Document]
    phrasebook: Phrasebook
    started: bool
    won: bool

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
            phrasebook=phrasebook,
            started=False,
            won=False
        )

    def start(self) -> str:
        self.started = True
        print(self)
        reply = self.officer_session.chat.get_last(ChatRole.ASSISTANT).content
        return self.country_session.from_english(reply, NORMAL_PRIORITY)

    @staticmethod
    def generate_documents(quenta: Quenta, session: ConstructedCountrySession) -> List[Document]:
        return [
            Passport.from_quenta(quenta),
            WorkPermit.from_quenta(quenta, session),
            EmploymentAgreement.from_quenta(quenta, session),
            TenancyAgreement.from_quenta(quenta, session)
        ]

    def process_officer(self, reply: str) -> str:
        if "%%SUCCESS%%" in reply:
            logger.debug("Winning condition met")
            self.won = True
        reply = reply.replace("%%SUCCESS%%", "")
        translation = self.country_session.from_english(reply, NORMAL_PRIORITY)
        return translation

    def say_to_officer(self, sentence: str) -> str:
        is_english = self.country_session.is_english(sentence, FORGET_PRIORITY)
        is_national = self.country_session.is_national(sentence, FORGET_PRIORITY)
        if is_national:
            translation = self.country_session.to_english(sentence, NORMAL_PRIORITY)
            reply = self.officer_session.say(translation, LanguageUnderstanding.NATIVE_CLEAR)
        elif is_english:
            reply = self.officer_session.say(sentence, LanguageUnderstanding.NON_NATIVE)
        else:
            reply = self.officer_session.say(sentence, LanguageUnderstanding.NATIVE_GIBBERISH)
        return self.process_officer(reply)

    def give_document(self, index: int) -> str:
        reply = self.officer_session.give_document(self.documents[index])
        return self.process_officer(reply)
