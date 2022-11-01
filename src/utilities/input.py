from __future__ import annotations

from typing import TYPE_CHECKING

from pynput.keyboard import Listener

if TYPE_CHECKING:
    from src.game import Game

movement = {
    "UP": (0,-1),
    "DOWN": (0,1),
    "LEFT": (-1,0),
    "RIGHT": (1,0),
    "U": (0,-1),
    "D": (0,1),
    "L": (-1,0),
    "R": (1,0),
    "W": (0,-1),
    "S": (0,1),
    "A": (-1,0),
    "D": (1,0),
    "KEY.UP": (0,-1),
    "KEY.DOWN": (0,1),
    "KEY.LEFT": (-1,0),
    "KEY.RIGHT": (1,0)
}

class InputHandler():

    def __init__(self, game: Game) -> None:
        """
        Input handler is responsible for reading a real player's realtime input to the keyboard.

        Args:
            game (Game): The game's overarching class, mainly used for game interaction with the human player.
        """
        self.game = game
        self.engine = self.game.engine

    def on_press(self, key):
        if str(key).upper() in movement:
            self.engine.bump(self.engine.player.pos, movement[str(key).upper()])
        elif str(key).upper() == "KEY.ESC":
            self.game.pause()
            raise SystemExit
        elif str(key).upper() == "KEY.CTRL_L":
            self.engine.cheat("godmode")
        return False

    def parse(self):
        with Listener(
            on_press=self.on_press,
            ) as listener:
            listener.join()