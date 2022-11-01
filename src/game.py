import copy

from pynput.keyboard import Listener

from src.utilities.input import InputHandler
from src.engine import Engine
from src.entities.entity_factory import player


class Game:
    def __init__(self, seed: int = 0, fixed_seed: bool = False) -> None:
        """
        Game class handles running the game from main.py

        Args:
            seed (int, optional): The seed for the level generation. Defaults to 0.
            fixed_seed (bool, optional): Set to true if you want to use a seed. Defaults to False.
        """
        self.player = copy.deepcopy(player)
        self.engine = Engine(self.player, seed, fixed_seed)
    
    def start(self) -> None:
        """
        Starts the game by creating an input handler and performing a game loop.
        """
        self.input_handler = InputHandler(game=self)
        while not self.engine.player.is_dead():
            self.engine.render()
            self.input_handler.parse()
            self.engine.handle_enemy_turns()
        print("You fought well, but you suck.")
    
    def quit(self) -> None:
        """
        Quits the game.
        """
        self.engine.player.hp = 0
        print("I can't believe you surrendered!")
    
    def on_press(self, key):
        if str(key).upper() == "KEY.ESC":
            print("         ! Game Resumed !")
            return False
        elif str(key).upper() == "KEY.ENTER":
            self.quit()
            return False
    
    def pause(self) -> None:
        """
        Pauses the game.
        """
        print("         ! Game is paused !")
        print("                 [Esc]: Resumes/Pauses game. ")
        print("                 [Enter]: Quits game when paused. ")
        with Listener(
            on_press=self.on_press,
            ) as listener:
            listener.join()