from __future__ import annotations

import numpy as np
import copy

from typing import Tuple, TYPE_CHECKING

import math

import time
import random
from src.world.level import Level
from src.entities.entity import AIFighter, Fighter, Item, Actor
from src.utilities.actions import Movement, Attack, Take
from src.utilities.pathfind import get_path_to
from datetime import datetime
 
if TYPE_CHECKING:
    from src.world.tile import Tile
 
class Engine:

    def __init__(self, player: Fighter, seed: int = 0, fixed_seed: bool = False, map_size: Tuple[int, int] = (15, 18)) -> None:
        """
        Engine Class is responsible for generating new levels, calculating field-of-vision, and
        handling enemy turns. Initialises seed (make sure to set fixed_seed to true when doing so.) and stage.

        Args:
            player (Fighter): Player of the game.
            seed (int, optional): Seed to generate from, passed to level constructor. Defaults to 0.
            fixed_seed (bool, optional): Set to true if seed is used, passed to level constructor. Defaults to False.
        """
        self.depth = 0
        self.player = player
        self.seed = seed
        self.fixed_seed = fixed_seed
        if self.fixed_seed == False:
            self.seed = datetime.now().microsecond + int(time.time())
            random.seed(datetime.now().microsecond + int(time.time()))
        self.next_level()
        
            
    def next_level(self) -> None:
        """
        Generates a new level for the dungeon. This is done by creating a new level completely,
        and creating the background and layout layers of the map.
        """
        self.seed = self.seed + self.seed      
        self.level = Level(15, 18, self.player, self.seed, self.fixed_seed)
        random.seed(datetime.now().microsecond + int(time.time()))
        
        min_rooms, max_rooms, min_room_size, max_room_size, num_enemies, num_potions = self.calculate_paramaters((15,18))
        
        self.level.carve(min_rooms, max_rooms, min_room_size, max_room_size, num_enemies, num_potions)
        self.background = copy.deepcopy(self.level)
        self.layout = copy.deepcopy(self.level)
        self.level.spawner(num_enemies, num_potions)
        self.clean_up()
        
        self.depth += 1

    def calculate_paramaters(self, map_size) -> None:
        """
        Calculates parameters for room and level generation to scale the difficulty with depth.
        """
        min_rooms = min(4, 3 + (self.depth-int(self.depth/4)))
        max_rooms = min(4, 3 + (self.depth - int(self.depth/4)))
        min_room_size = 4
        max_room_size = min(5, 4 + self.depth-int(self.depth/4))
        num_enemies = min(6, 2 + (self.depth))
        num_potions = min(6, 2 + int(self.depth/2))
        return min_rooms, max_rooms, min_room_size, max_room_size, num_enemies, num_potions
        
    def clean_up(self) -> None:
        """
        Checks if entities exist in their given positions, if not remove them.
        """
        entities_clean = copy.copy(self.level.entities)
        for entity in entities_clean:
            if isinstance(self.level.tiles[entity.pos[0], entity.pos[1]], AIFighter):
                continue
            else:
                self.level.entities.remove(entity)
    
    def handle_enemy_turns(self) -> None:
        """
        Handles enemies turns by looping over all enemies in previously explored tiles and sending
        them on a path to the player. When player is dead return because game is over.
        """
        enemies = copy.deepcopy(self.level.entities)
        for entity in enemies:
            if isinstance(entity, AIFighter) and self.layout.tiles[entity.pos].explored:
                path = get_path_to(entity, self.player.pos, self.level)
                path = (path[1] - entity.pos[0], path[0] - entity.pos[1])
                self.bump(entity.pos, path)
                if self.player.is_dead():
                    return

    def bump(self, start: Tuple[int, int], change: Tuple[(1 | 0), (1 | 0)]) -> Tuple[type, (Fighter | Item | Tile)]:
        """
        Moves character in x and y dimension and then performs an action depending on what is at the destination.

        Args:
            start (Tuple[int, int]): Starting position of entity bumping.
            change (Tuple[(1 | 0), (1 | 0)]): Change in x and y dimensions.

        Returns:
            Tuple[type, (Fighter | Item | Tile)]: A tuple including type of action taken and what was on the destination tile.
        """
        # Grabs entity to_move and whatever is on the destination tile.
        to_move = self.level.tiles[start]
        change_x, change_y = change
        dest = self.level.tiles[start[0]+change_x, start[1]+change_y]
        dest_bg = self.layout.tiles[start[0]+change_x, start[1]+change_y]
        
        # Makes enemies not attack each other.
        if isinstance(dest, AIFighter) and isinstance(to_move, AIFighter):
            return
        
        # Attacks in case enemy is in destination.
        elif isinstance(dest, Actor):
            action = Attack(self)
                    
        # Otherwise, checks if item is ahead
        elif (isinstance(dest, Item) or isinstance(dest_bg,Item)) and isinstance(to_move, Fighter):
            action = Take(self)
        
        else:
            action = Movement(self)
        
        destc = copy.deepcopy(dest)
        
        action.perform(start, change)
        return type(action), dest
        
    def fov(self) -> None:
        """
        Calculates player's field of vision by marking 3 tiles to the right, top, buttom, and left as explored.
        """
        
        for y in range(max(0,self.player.pos[1]-3), min(self.level.height, self.player.pos[1]+3)):
            for x in range(max(0,self.player.pos[0]-3), min(self.level.width, self.player.pos[0]+3)):
                self.layout.tiles[x,y].explored = True
                
    def render(self) -> None:
        """
        Renders game and runs fov function. Only renders explored tiles.
        """
        self.fov()
        for y in range(self.level.height):
            for x in range(self.level.width):
                if self.layout.tiles[x,y].explored:
                    print(self.level.tiles[x,y].char, end="  ")
                else:
                    print("   ", end="")
            print("\n")
        print("===" * self.level.width)
        print("HP:", self.player.hp, "/ 20" )
    
    def cheat(self, cheat: str) -> None:
        """
        Cheats used for debugging.
        """
        if cheat == "godmode":
            for y in range(self.level.height):
                for x in range(self.level.width):
                    self.layout.tiles[x,y].explored = True
            self.player.hp = 5000