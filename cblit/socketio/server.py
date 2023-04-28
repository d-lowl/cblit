from typing import Dict, Any
import asyncio
import socketio
from sanic import Sanic

from cblit.game.game import Game

games_event_loop = asyncio.new_event_loop()
games: Dict[str, Game] = {}

sio = socketio.AsyncServer(async_mode='sanic')

app = Sanic(name="cblit")
sio.attach(app)


def generate_game(sid: str) -> None:
    async def _generate_game() -> None:
        games[sid] = await Game.generate()
        print("game generated for: ", sid)

    asyncio.get_running_loop().create_task(_generate_game())


@sio.event
async def connect(sid: str, environ: Any, auth: Any) -> None:
    generate_game(sid)


@sio.event
def disconnect(sid: str) -> None:
    print('disconnect ', sid)


@sio.event
def test(sid: str, data: str) -> None:
    print("test event: ", sid, data)


if __name__ == "__main__":
    app.run()
