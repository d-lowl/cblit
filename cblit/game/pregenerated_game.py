"""Pregenerated Game."""
import os
import random
from typing import Self, cast

import pydantic
from pydantic import BaseModel

from cblit.game.game import Game
from cblit.session.country import ConstructedCountrySession, Country
from cblit.session.immigrant.document import Document
from cblit.session.immigrant.immigrant import Immigrant
from cblit.session.immigrant.quenta import Quenta
from cblit.session.language.phrasebook import Phrasebook
from cblit.session.language.translator import ConlangEntry, TranslatorSession
from cblit.session.officer import OfficerSession


class PregeneratedGame(BaseModel):
    """Pregenerated Game."""
    country: Country
    quenta: Quenta
    documents: list[Document]
    phrasebook: Phrasebook

    @classmethod
    def from_game(cls, game: Game) -> Self:
        """Turn a game into a savable pregenrated game.

        Args:
            game (Game): to save

        Returns:
            PregeneratedGame:
        """
        return cls(
            country=game.country,
            quenta=game.immigrant.quenta,
            documents=game.immigrant.documents,
            phrasebook=game.phrasebook
        )

    @classmethod
    def get_random(cls) -> Self:
        """Get random previously generated game.

        Returns:
            PregeneratedGame:
        """
        filenames = os.listdir("pregenerated_games/")
        filename = os.path.join("pregenerated_games", random.choice(filenames))
        return cast(Self, pydantic.parse_file_as(path=filename, type_=PregeneratedGame))

    def to_game(self) -> Game:
        """Turn pregenerated game into a Game instance.

        Returns:
            Game: game
        """
        country_session = ConstructedCountrySession.instance()
        country = self.country

        initial_conlang_entry = ConlangEntry(
            english=country.example_sentence_translation,
            conlang=country.example_sentence,
        )
        translator_session = TranslatorSession(
            country.language_name,
            initial_conlang_entry,
        )
        for entry in self.phrasebook.phrases:
            translator_session.save_translation(entry)
        for document in self.documents[1:]:
            translator_session.save_translation(
                ConlangEntry(english=document.officer_representation, conlang=document.player_representation)
            )

        phrasebook = self.phrasebook
        self.phrasebook.phrases += [initial_conlang_entry]

        officer_session = OfficerSession()

        immigrant = Immigrant(quenta=self.quenta, documents=self.documents)

        return Game(
            country_session=country_session,
            country=country,
            translator_session=translator_session,
            officer_session=officer_session,
            immigrant=immigrant,
            phrasebook=phrasebook,
            started=False,
            won=False
        )
