import asyncio
from collections.abc import Coroutine
from typing import Any

import socketio

from cblit.game.game import Game
from cblit.socketio.messages import DocumentPayload, DocumentsPayload, SayPayload, WaitPayload, WinPayload


def aiorun(coroutine: Coroutine[Any, Any, Any]) -> None:
    asyncio.get_running_loop().create_task(coroutine)


class GameSession:
    session_id: str
    _game: Game | None = None

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id

    async def initialise(self) -> None:
        self._game = await Game.generate()

    @property
    def game(self) -> Game:
        if self._game is None:
            raise ValueError("Game session is not initialised")
        return self._game

    async def start(self) -> str:
        return await self.game.start()


class GameSessionManager:
    server: socketio.AsyncServer
    sessions: dict[str, GameSession] = {}

    def __init__(self, server: socketio.AsyncServer) -> None:
        self.server = server

    def get_session(self, session_id: str) -> GameSession:
        if session_id not in self.sessions:
            raise Exception(f"'{session_id}' game session does not exist")
        return self.sessions[session_id]

    async def reply(self, session_id: str, message: str) -> None:
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
        await self.server.emit(
            "wait",
            WaitPayload(wait).to_json(),
            session_id
        )

    async def send_documents(self, session_id: str) -> None:
        documents = self.get_session(session_id).game.immigrant.documents
        payload = DocumentsPayload([DocumentPayload(document.player_representation) for document in documents])
        await self.server.emit(
            "documents",
            payload.to_json(),
            session_id
        )

    async def send_phrasebook(self, session_id: str) -> None:
        phrasebook = self.get_session(session_id).game.phrasebook
        await self.server.emit(
            "phrasebook",
            phrasebook.to_json(),
            session_id
        )

    async def _give_documents(self, session_id: str, doc_id: int) -> None:
        session = self.get_session(session_id)
        reply = await session.game.give_document(doc_id)
        await self.reply(session_id, reply)

    def give_documents(self, session_id: str, doc_id: int) -> None:
        """Give document to the officer in a game.

        :param session_id:
        :param doc_id:
        """
        aiorun(self._give_documents(session_id, doc_id))

    async def _say(self, session_id: str, text: str) -> None:
        session = self.get_session(session_id)
        reply = await session.game.say_to_officer(text)
        await self.reply(session_id, reply)

    def say(self, session_id: str, text: str) -> None:
        """Say to the officer in a game.

        :param session_id: player's session ID
        :param text: text to say
        """
        aiorun(self._say(session_id, text))

    async def _create_session(self, session_id: str) -> None:
        self.sessions[session_id] = GameSession(session_id)
        await self.tell_to_wait(session_id, True)
        await self.sessions[session_id].initialise()
        start_officer_line = await self.sessions[session_id].start()
        await asyncio.gather(
            self.reply(session_id, start_officer_line),
            self.send_documents(session_id),
            self.send_phrasebook(session_id)
        )
        await self.tell_to_wait(session_id, False)

    def create_session(self, session_id: str) -> None:
        """Create game session for a session ID.

        It will return, and then generate a game in the background.
        When the game is generated the player will be notified.

        :param session_id: player's session ID
        """
        aiorun(self._create_session(session_id))
