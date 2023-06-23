"""Server module."""
import os.path
from typing import Any

import socketio
from sanic import Sanic

from cblit.game.game import Game
from cblit.socketio.game import GameSessionManager
from cblit.socketio.messages import GiveDocumentPayload, SayPayload

static_path = os.path.join(os.path.dirname(__file__), "static")

games: dict[str, Game] = {}

sio = socketio.AsyncServer(async_mode="sanic")

app = Sanic(name="cblit")
app.static("/", os.path.join(static_path, "index.html"), name="game")
app.static("/static/", static_path, name="statics")
sio.attach(app)

session_manager = GameSessionManager(sio)


def generate_game(sid: str) -> None:
    """Start generating a game for a session ID.

    Args:
        sid (str): session ID
    """
    session_manager.create_session(sid)


@sio.event
async def connect(sid: str, environ: Any, auth: Any) -> None:
    """Connect event handler.

    Args:
        sid (str): session ID
        environ (Any): unused
        auth (Any): unused
    """
    generate_game(sid)


@sio.event
def disconnect(sid: str) -> None:
    """Disconnect event handler.

    Args:
        sid (str): session ID
    """
    print("disconnect ", sid)


@sio.event
def say(sid: str, data: str) -> None:
    """Say event handler.

    Args:
        sid (str): session ID
        data (str): raw event data
    """
    payload = SayPayload.from_json(data)
    session_manager.say(sid, payload.message)


@sio.event
def give_document(sid: str, data: str) -> None:
    """Give documents event handler.

    Args:
        sid (str): session ID
        data (str): raw event data
    """
    payload = GiveDocumentPayload.from_json(data)
    session_manager.give_documents(sid, payload.index)


if __name__ == "__main__":
    app.run()
