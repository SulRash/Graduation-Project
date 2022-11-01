from __future__ import annotations

import numpy as np
import random
import copy
from datetime import datetime

from typing import List, TYPE_CHECKING, Tuple

from src.world.tile import wall, floor
from src.world.room import RectangleRoom
from src.entities.entity_factory import zombie, vampire, exit, health_potion

if TYPE_CHECKING:
    from src.entities.entity import Fighter

class Level:

    def __init__(self, height: int, width: int, player: Fighter, seed: int = 0, fixed_seed: bool = False) -> None:
        """
        Initialises level by taking the height and width of the desired map (usually fixed for the agent's observation space), 
        the game's player, and a seed if desired. To use the seed please set fixed_seed to True.
        
        To-Do?:
            - Remove tether to agent's observation space by setting a max size that we can cut out of.

        Args:
            height (int): Height for console view.
            width (int): Width for console view.
            player (Player): Player of the game.
            seed (int): Seed to randomise with.
            fixed_seed (bool, optional): If you want to use a specific seed, this must be set true. Defaults to False.
        """
        self.player = player
        self.height = height
        self.width = width
        self.tiles = np.array([[wall]*height]*width)
        for y in range(height):
            for x in range(width):
                self.tiles[x,y] = copy.deepcopy(wall)
        self.entities = set([self.player])
        
        if fixed_seed:
            self.seed = seed
            random.seed(self.seed)
        else:
            random.seed(datetime.now().microsecond)
            self.seed = seed
        self.seedings = 0

    def tunnel(self, currRoom: RectangleRoom) -> None:
        """
        Tunnels between the current room and the previous one.

        Args:
            currRoom (RectangleRoom): Current room to generate tunnel from.
        """

        if len(self.rooms) >= 1:
            curr_x, curr_y = currRoom.center

            prev_x, prev_y = self.rooms[len(self.rooms)-1].center

            # We give the tunnel a 50% chance to start horizontally
            if random.randint(0,1) == 1:
                for x in range(min(prev_x, curr_x), max(prev_x, curr_x) + 1):
                    self.tiles[x, prev_y] = copy.deepcopy(floor)
                    """if self.tiles[x, prev_y-1].char == "#" and self.tiles[x, prev_y+1].char == "#":
                        self.tiles[x, prev_y] = copy.deepcopy(tunnel)"""
                        
                for y in range(min(prev_y, curr_y), max(prev_y, curr_y) + 1):
                    self.tiles[curr_x, y] = copy.deepcopy(floor)
                    """if self.tiles[curr_x+1, y].char == "#" and self.tiles[curr_x-1, y].char == "#":
                        self.tiles[curr_x, y] = copy.deepcopy(tunnel)"""
                    
            else:
                for y in range(min(prev_y, curr_y), max(prev_y, curr_y) + 1):
                    self.tiles[prev_x, y] = copy.deepcopy(floor)
                    """if self.tiles[prev_x+1, y].char == "#" and self.tiles[prev_x-1, y].char == "#":
                        self.tiles[prev_x, y] = copy.deepcopy(tunnel)"""
                    
                for x in range(min(prev_x, curr_x), max(prev_x, curr_x) + 1):
                    self.tiles[x, curr_y] = copy.deepcopy(floor)
                    """if self.tiles[x, curr_y+1].char == "#" and self.tiles[x, curr_y-1].char == "#":
                        self.tiles[x, curr_y] = copy.deepcopy(tunnel)"""
    
    def carve(self, min_rooms: int, max_rooms: int, min_room_size: int, max_room_size: int,  num_enemies: int, num_potions: int) -> None:
        """
        Carves out rooms in the dungeon according to parameters set by the engine (scales for difficulty).

        Args:
            min_rooms (int): Minimum rooms to generate.
            max_rooms (int): Maximum rooms to generate.
            min_room_size (int): Minimum room size.
            max_room_size (int): Maximum room size
            num_enemies (int): Number of enemies
            num_potions (int): Number of potions.
        """

        self.rooms = []
        rooms_so_far = 0

        num_rooms = random.randint(min_rooms, max_rooms)
        random.seed(self.seed + self.seedings)
        self.seedings += 1

        while len(self.rooms) < min_rooms:
            
            width = random.randint(min_room_size, max_room_size)
            random.seed(self.seed + self.seedings)
            self.seedings += 1
            
            height = random.randint(min_room_size, max_room_size)
            random.seed(int(self.seed + self.seedings))
            self.seedings -= 1
            
            x1 = random.randint(0, self.width - width - 1)
            random.seed(self.seed + self.seedings)
            self.seedings += 1
            
            y1 = random.randint(0, self.height - height - 1)
            random.seed(int(self.seed + self.seedings))
            self.seedings += 1
            
            room = RectangleRoom(x1, y1, width, height)

            if any(room.intersect(checked_room) for checked_room in self.rooms):
                continue

            self.tiles[room.space] = copy.deepcopy(floor)
            
            self.tunnel(currRoom=room)

            self.rooms.append(room)
        
            rooms_so_far += 1
    
    def get_exit(self) -> Tuple[int, int]:
        return self.rooms[len(self.rooms)-1].center
    
    def spawner(self, num_enemies: int, num_potions: int) -> None:
        """
        Spawns player, enemies, and potions into the map.

        Args:
            num_enemies (int): Number of enemies to spawn.
            num_potions (int): Number of potions to spawn.
        """
        
        
        # Spawns player in first room.
        first_room = self.rooms[0]
        self.tiles[first_room.center] = self.player
        player_x, player_y = first_room.center
        self.player.set_pos(player_x, player_y)
        
        # Spawns exit in last room.
        last_room = self.rooms[len(self.rooms)-1]
        self.tiles[last_room.center] = copy.deepcopy(exit)
        
        # Spawns all potions and enemies on map.
        while num_enemies > 0 or num_potions > 0:
            room_number = random.randint(0, len(self.rooms)-1)
            random.seed(self.seed + self.seedings)
            self.seedings += 1
            
            room = self.rooms[room_number]
            
            # We get the room's x and y limits, and pick a random spot in the room to spawn it in.
            room_start_x = room.space[0].start
            room_start_y = room.space[1].start
            room_end_x = room.space[0].stop
            room_end_y = room.space[1].stop
            
            spawn_location_x = random.randint(room_start_x, room_end_x-1)
            random.seed(self.seed + self.seedings)
            self.seedings += 1
            
            spawn_location_y = random.randint(room_start_y, room_end_y-1)
            random.seed(self.seed + self.seedings)
            self.seedings += 1
            
            
            # If a spawned entity exists already, continue.
            if self.tiles[spawn_location_x, spawn_location_y].char != ".":
                continue
            
            if num_enemies > 0:
                
                if random.randint(0,2) == 0:
                    enemy = copy.deepcopy(vampire)
                else:
                    enemy = copy.deepcopy(zombie)
                
                enemy.set_pos(spawn_location_x, spawn_location_y)
                self.entities.add(enemy)
                self.tiles[spawn_location_x, spawn_location_y] = enemy
                num_enemies -= 1
                
            elif num_potions > 0:
                
                potion = copy.deepcopy(health_potion)
                potion.set_pos(spawn_location_x, spawn_location_y)
                self.entities.add(potion)
                self.tiles[spawn_location_x, spawn_location_y] = potion
                num_potions -= 1
            
            # Accounts for two randomisations above
            random.seed(self.seed + self.seedings)
            self.seedings += 1