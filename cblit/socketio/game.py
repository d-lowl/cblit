"""Game module."""
import asyncio
from collections.abc import Coroutine
from typing import Any

import socketio

from cblit.game.game import Game
from cblit.game.pregenerated_game import PregeneratedGame
from cblit.session.country import Country
from cblit.socketio.messages import BriefPayload, DocumentPayload, DocumentsPayload, SayPayload, WaitPayload, WinPayload


def aiorun(coroutine: Coroutine[Any, Any, Any]) -> None:
    """Run a coroutine to completion.

    Args:
        coroutine (Coroutine): coroutine to run
    """
    asyncio.get_running_loop().create_task(coroutine)


class GameSession:
    """Game session."""
    session_id: str
    _game: Game | None = None

    def __init__(self, session_id: str) -> None:
        """Initialise session.

        Args:
            session_id (str): socket.io session ID
        """
        self.session_id = session_id

    async def initialise(self) -> None:
        """Asynchronously initialise."""
        self._game = PregeneratedGame.get_random().to_game()

    @property
    def game(self) -> Game:
        """Get game instance.

        Returns:
            Game: game instance
        """
        if self._game is None:
            raise ValueError("Game session is not initialised")
        return self._game

    async def start(self) -> str:
        """Start the game.

        Returns:
            str: Initial officer's saying
        """
        return await self.game.start()


class GameSessionManager:
    """Game session manager.

    Class that manages mapping between socket.io sessions and game sessions.
    """
    server: socketio.AsyncServer
    sessions: dict[str, GameSession] = {}

    def __init__(self, server: socketio.AsyncServer) -> None:
        """Initialise with socket.io server.

        Args:
            server (socketio.AsyncServer): server to use
        """
        self.server = server

    def get_session(self, session_id: str) -> GameSession:
        """Get session by session ID.

        Args:
            session_id (str): session ID

        Returns:
            GameSession: game session

        Raises:
            Exception: when game session does not exist
        """
        if session_id not in self.sessions:
            raise Exception(f"'{session_id}' game session does not exist")
        return self.sessions[session_id]

    async def reply(self, session_id: str, message: str) -> None:
        """Emit officer's reply.

        Args:
            session_id (str): session ID to reply to
            message (str): officer's reply message
        """
        session = self.get_session(session_id)
        await self.server.emit(
            "say",
            SayPayload(
                who="officer",
                message=message
            ).to_json(),
            session_id
        )
        await self.server.emit(
            "win",
            WinPayload(
                won=session.game.won
            ).to_json(),
            session_id
        )

    async def tell_to_wait(self, session_id: str, wait: bool) -> None:
        """Send the client the waiting status.

        Args:
            session_id (str): session ID
            wait (bool): waiting status
        """
        await self.server.emit(
            "wait",
            WaitPayload(wait).to_json(),
            session_id
        )

    async def send_documents(self, session_id: str) -> None:
        """Send generated documents.

        Args:
            session_id (str): session ID to send to
        """
        documents = self.get_session(session_id).game.immigrant.documents
        payload = DocumentsPayload([DocumentPayload(document.player_representation) for document in documents])
        await self.server.emit(
            "documents",
            payload.to_json(),
            session_id
        )

    async def send_phrasebook(self, session_id: str) -> None:
        """Send generated phrasebook.

        Args:
            session_id (str): session ID to send to
        """
        phrasebook = self.get_session(session_id).game.phrasebook
        await self.server.emit(
            "phrasebook",
            phrasebook.json(),
            session_id
        )

    async def send_brief(self, session_id: str, country: Country) -> None:
        """Send generated country information.

        Args:
            session_id (str): session ID to send to
            country (Country): the generated country
        """
        brief = BriefPayload(
            country_name=country.country_name,
            language_name=country.language_name,
            country_description=country.country_description
        )
        await self.server.emit(
            "brief",
            brief.to_json(),
            session_id
        )


    async def _give_documents(self, session_id: str, doc_id: int) -> None:
        """Private 'give documents' event handler.

        Args:
            session_id (str): session ID from which the event is coming from
            doc_id (int): document ID to give
        """
        session = self.get_session(session_id)
        await self.tell_to_wait(session_id, True)
        reply = await session.game.give_document(doc_id)
        await self.reply(session_id, reply)
        await self.tell_to_wait(session_id, False)

    def give_documents(self, session_id: str, doc_id: int) -> None:
        """Give document to the officer in a game.

        Args:
            session_id (str): session ID from which the event is coming from
            doc_id (int): document ID to give
        """
        aiorun(self._give_documents(session_id, doc_id))

    async def _say(self, session_id: str, text: str) -> None:
        """Private 'say' event handler.

        Args:
            session_id (str): session ID from which the event is coming from
            text (str): text to say
        """
        session = self.get_session(session_id)
        await self.tell_to_wait(session_id, True)
        reply = await session.game.say_to_officer(text)
        await self.reply(session_id, reply)
        await self.tell_to_wait(session_id, False)

    def say(self, session_id: str, text: str) -> None:
        """Say to the officer in a game.

        Args:
            session_id (str): session ID from which the event is coming from
            text (str): text to say
        """
        aiorun(self._say(session_id, text))

    async def _create_session(self, session_id: str) -> None:
        """Private game session creation handler.

        Args:
            session_id (str): session ID from which the request is coming from
        """
        self.sessions[session_id] = GameSession(session_id)
        await self.tell_to_wait(session_id, True)
        await self.sessions[session_id].initialise()
        start_officer_line = await self.sessions[session_id].start()
        await asyncio.gather(
            self.reply(session_id, start_officer_line),
            self.send_documents(session_id),
            self.send_phrasebook(session_id),
            self.send_brief(session_id, self.sessions[session_id].game.country)
        )
        await self.tell_to_wait(session_id, False)

    def create_session(self, session_id: str) -> None:
        """Create game session for a session ID.

        It will return, and then generate a game in the background.
        When the game is generated the player will be notified.

        Args:
            session_id (str): session ID from which the request is coming from
        """
        aiorun(self._create_session(session_id))
