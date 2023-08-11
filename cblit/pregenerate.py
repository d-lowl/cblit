"""Script to pregenerate games."""
import asyncio
import time

from loguru import logger

from cblit.game.game import Game
from cblit.game.pregenerated_game import PregeneratedGame


async def pregenerate_game() -> None:
    """Pregenerate a game."""
    start_time = time.time()
    filename = f"pregen_{int(start_time)}.json"
    logger.info(f"Pregenerating {filename}")

    try:
        game = await Game.generate()
        pregenerated_game = PregeneratedGame.from_game(game)
        game_json = pregenerated_game.json(indent=2)

        with open(filename, "w") as f:
            f.write(game_json)

        finish_time = time.time()
        logger.info(f"Finished generation in {finish_time - start_time} seconds")
    except Exception as e:
        logger.error(f"Error occured: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for i in range(1000):
        logger.info(f"Pregenerating #{i}")
        loop.run_until_complete(pregenerate_game())

    logger.info("Done")
