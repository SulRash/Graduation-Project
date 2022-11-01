from __future__ import annotations

from typing import Tuple, TYPE_CHECKING
import copy

from src.world.tile import floor
from src.entities.entity_factory import corpse

if TYPE_CHECKING:
    from src.engine import Engine

class Action:
    def __init__(self, engine: Engine) -> None:
        """
        Action is the base class of all action classes.

        Args:
            engine (Engine): The game engine.
        """
        self.engine = engine
    
    def perform(self, start: Tuple[int, int], change: Tuple[int, int]):
        """
        Perform's the action's action.

        Args:
            start (Tuple[int, int]): Entity performing the action's location.
            change (Tuple[int, int]): The change in x and y coordinates to lead to the destination.

        Raises:
            NotImplementedError: Not implemented because this base class should never be invoked.
        """
        raise NotImplementedError

class Movement(Action):
    def __init__(self, engine):
        super().__init__(engine)
    
    def perform(self, start, change):
        to_move = self.engine.level.tiles[start]
        change_x, change_y = change
        dest = self.engine.level.tiles[start[0]+change_x, start[1]+change_y]
        
        # If movement is blocked don't move and waste a turn.
        if dest.blocks_movement:
            return
        
        to_move.move(change_x, change_y)
        self.engine.level.tiles[start] = self.engine.background.tiles[start]
        self.engine.level.tiles[to_move.pos] = to_move

class Attack(Action):
    def __init__(self, engine):
        super().__init__(engine)
    
    def perform(self, start, change):
        to_move = self.engine.level.tiles[start]
        change_x, change_y = change
        dest = self.engine.level.tiles[start[0]+change_x, start[1]+change_y]
        
        # Attacks character in destination tile
        dest.damage(to_move.attack)
        if dest.is_dead():
            try:
                self.engine.level.entities.remove(dest)
            except KeyError:
                return
            self.engine.level.tiles[start[0]+change_x, start[1]+change_y], self.engine.background.tiles[start[0]+change_x, start[1]+change_y] = copy.deepcopy(corpse), copy.deepcopy(corpse)
            if to_move == self.engine.player:
                if dest.char == "z":
                    self.engine.player.gold += 1
                elif dest.char == "v":
                    self.engine.player.gold += 5
        
class Take(Action):
    def __init__(self, engine):
        super().__init__(engine)
    
    def perform(self, start, change):
        to_move = self.engine.level.tiles[start]
        change_x, change_y = change
        dest = self.engine.level.tiles[start[0]+change_x, start[1]+change_y]
        
        self.engine.level.tiles[start[0]+change_x, start[1]+change_y], self.engine.background.tiles[start[0]+change_x, start[1]+change_y] = copy.deepcopy(floor), copy.deepcopy(floor)
        dest.perform(self.engine)
        
        