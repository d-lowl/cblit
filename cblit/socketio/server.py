import os.path
from typing import Dict, Any
import socketio
from sanic import Sanic

from cblit.game.game import Game
from cblit.socketio.game import GameSessionManager
from cblit.socketio.messages import Message, SayPayload, GiveDocumentPayload

static_path = os.path.join(os.path.dirname(__file__), "static")
print(static_path)

games: Dict[str, Game] = {}

sio = socketio.AsyncServer(async_mode='sanic')

app = Sanic(name="cblit")
app.static("/", os.path.join(static_path, "index.html"), name="game")
app.static("/static/", static_path, name="statics")
sio.attach(app)

session_manager = GameSessionManager(sio)


def generate_game(sid: str) -> None:
    session_manager.create_session(sid)


@sio.event
async def connect(sid: str, environ: Any, auth: Any) -> None:
    generate_game(sid)


@sio.event
def disconnect(sid: str) -> None:
    print('disconnect ', sid)


@sio.event
def say(sid: str, data: str) -> None:
    print(data)
    Message[SayPayload].deserialize(data)


@sio.event
def give_document(sid: str, data: str) -> None:
    print(data)
    payload = GiveDocumentPayload.from_json(data)
    session_manager.give_documents(sid, payload.index)



if __name__ == "__main__":
    app.run()
