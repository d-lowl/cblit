from typing import Self

from cblit.game.game import Game


class GameCliWrapper:
    game: Game

    def __init__(self, game: Game):
        self.game = game

    @classmethod
    def generate(cls) -> Self:
        return cls(
            game=Game.generate()
        )
