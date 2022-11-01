# Gym Environment

from gym.spaces import Discrete
from gym.spaces.box import Box
from gym import Env

from stable_baselines3.common.evaluation import evaluate_policy

from datetime import datetime
from typing import List, Tuple

import time

import random
from math import ceil
import numpy as np
import copy
import multiprocessing as mp
from multiprocessing import Pool

from src.engine import Engine
from src.utilities.actions import Take, Attack
from src.entities.entity_factory import player
from src.utilities.pathfind import get_path_to

from PIL import Image, ImageDraw, ImageFont

# Translates discrete action to up, down, left, and right.
action_translator = {
    0: (1,0),
    1: (-1,0),
    2: (0,1),
    3: (0,-1)
}

# Translates level from characters to numbers for agent.
level_translator = {
    "#": 0,
    ".": 2,
    ">": 4,
    "@": 1,
    "+": 3,
    "z": -2,
    "v": -3,
    "q": -1,
    " ": -4
}

class RLEnv(Env):
    
    monospace = ImageFont.truetype("freemono.ttf",16)
    
    def __init__(self, seed: int = 0, to_image: bool = False, fixed_seed: bool = False, perfect_info: bool = True, map_size: Tuple[int, int] = (15, 18)) -> None:
        """
        RogueLike Reinforcement Learning Environment.

        Args:
            seed (int, optional): Seed if desired. Defaults to 0.
            fixed_seed (bool, optional): Write as true if you want to run with seed. Defaults to False.
        """
        # Necessary for game functionality:
        self.player = copy.deepcopy(player)
        self.fixed_seed = fixed_seed
        self.seed_num = seed
        self.perfect_info = perfect_info
        self.engine = Engine(self.player, self.seed_num, self.fixed_seed)
        
        # Necessary for environment functionality:
        self.to_image = to_image
        self.action_space = Discrete(4)
        
        if to_image:
            self.observation_space = Box(low=0, high=255, shape=(280,180,3), dtype=np.uint8) 
            self.agent_view = np.array([[[0]*3]*(280)]*(180))
        else:
            if perfect_info:
                self.observation_space = Box(low=-3, high=4, shape=((self.engine.level.height+1),self.engine.level.width), dtype=np.int_) 
                self.agent_view = np.array([[0]*(self.engine.level.width)]*(self.engine.level.height+1))
            else:
                self.observation_space = Box(low=-4, high=4, shape=((self.engine.level.height+1),self.engine.level.width), dtype=np.int_) 
                self.agent_view = np.array([[0]*(self.engine.level.width)]*(self.engine.level.height+1))
                
        # Necessary for reward calculation:
        self.time_spent = 0
        self.path_reward = 0
        self.last_hp = copy.deepcopy(self.engine.player.hp)
        self.explored_reward = 0
        
        # Necessary for formal logs:
        self.exits_taken = 0
        self.enemies_killed = 0
        self.potions_taken = 0

    def set_seed(self, seed: int = 0) -> None:
        """
        Sets seed and changes fixed_seed to True to allow for seed usage.
        
        Args:
            seed (int): Seed for random generators.
        
        To-Do:
            - Think about adding a system where the seed changes every 10 or 20 runs.
        """
        self.seed_num = seed
        self.fixed_seed = True
            

    def translate_map_to_image(self) -> Tuple[List[List[int]], dict]:
        """
        Translates map by characters into an image (for use in a convolutional neural network).

        Returns:
            Tuple[List[List[int]], dict]: Tuple of the agent's map and info collected during translation.
        """
        
        # Initialises info to be empty per check through
        info = {
            "enemies": 0,
            "potions": 0,
            "gold": self.engine.player.gold,
            "player health": self.engine.player.hp,
            #"exits taken": 0,
            "map": "",
            "agent view": "",
            "exits taken": 0
        }
        
        level_string = ""
        
        # Loops over actual map to translate it into the agent's view.
        for y in range(self.engine.level.height):
            for x in range(self.engine.level.width):

                # Handles whether the agent has perfect or imperfect information.
                if self.perfect_info:
                    level_string += self.engine.level.tiles[x,y].char
                else:
                    if self.engine.layout.tiles[x,y].explored:
                        level_string += self.engine.level.tiles[x,y].char
                    else:
                        level_string += " "
                
                # Adds enemies and potions to info for better logs
                if self.engine.level.tiles[x,y].char == "+":
                    info["potions"] += 1
                elif self.engine.level.tiles[x,y].char == "v" or self.engine.level.tiles[x,y].char == "z":
                    info["enemies"] += 1
                if self.engine.level.tiles[x,y].char == ">":
                    self.exit_location = (x,y)
                    
                # For rewarding agent for exploring tiles
                if self.engine.layout.tiles[x,y].explored and self.engine.level.tiles[x,y].char == "." and self.engine.layout.tiles[x,y].already_explored == False:
                    self.explored_reward += 1
                    self.engine.layout.tiles[x,y].already_explored = True
                
                # Build map as well for logs
                info["map"] += f"{self.engine.level.tiles[x,y].char}  "
                info["agent view"] += f"{self.agent_view[y,x]}  "
            
            level_string += "\n"
            info["map"] += "\n"
            info["agent view"] += "\n"
        info["map"] += "\n\n"
        info["agent view"] += "\n\n"
        
        level_string += str(self.engine.player.hp)
        level_string += "   "
        level_string += str(self.engine.depth)
        level_string += "   "
        level_string += str(self.engine.player.gold)
        
        img = Image.new('RGB', (180, 280), color = 0)
        
        image = ImageDraw.Draw(img)
        image.text((0,0), level_string, font=self.monospace, fill=(255, 255, 255))
        self.agent_view = np.array(img)
        img.close()

        return self.agent_view, info
    
    def translate_map_to_numbers(self) -> Tuple[List[List[int]], dict]:
        """
        Translates map by characters into integers.

        Returns:
            Tuple[List[List[int]], dict]: Tuple of the agent's map and info collected during translation.
        """
        
        # Initialises info to be empty per check through
        info = {
            "enemies": 0,
            "potions": 0,
            "gold": self.engine.player.gold,
            "player health": self.engine.player.hp,
            #"exits taken": 0,
            "map": "",
            "agent view": "",
            "exits taken": 0
        }
        
        # Loops over actual map to translate it into the agent's view.
        for y in range(self.engine.level.height):
            for x in range(self.engine.level.width):

                # Handles whether the agent has perfect or imperfect information.
                if self.perfect_info:
                    self.agent_view[y,x] = level_translator[ self.engine.level.tiles[x,y].char ]
                else:
                    if self.engine.layout.tiles[x,y].explored:
                        self.agent_view[y,x] = level_translator[ self.engine.level.tiles[x,y].char ]
                    else:
                        self.agent_view[y,x] = level_translator[" "]
                
                # Adds enemies and potions to info for better logs
                if self.engine.level.tiles[x,y].char == "+":
                    info["potions"] += 1
                elif self.engine.level.tiles[x,y].char == "v" or self.engine.level.tiles[x,y].char == "z":
                    info["enemies"] += 1
                elif self.engine.level.tiles[x,y].char == ">":
                    self.exit_location = (x,y)
                    
                # For rewarding agent for exploring tiles
                if self.engine.layout.tiles[x,y].explored and self.engine.level.tiles[x,y].char == "." and self.engine.layout.tiles[x,y].already_explored == False:
                    self.explored_reward += 1
                    self.engine.layout.tiles[x,y].already_explored = True
                
                # Build map as well for logs
                info["map"] += f"{self.engine.level.tiles[x,y].char}  "
                info["agent view"] += f"{self.agent_view[y,x]}  "
            info["map"] += "\n"
            info["agent view"] += "\n"
        info["map"] += "\n\n"
        info["agent view"] += "\n\n"
        
        self.agent_view[self.engine.level.height, 0] = self.engine.player.hp
        self.agent_view[self.engine.level.height, 1] = self.engine.depth
        self.agent_view[self.engine.level.height, 2] = self.engine.player.gold

        return self.agent_view, info

    def step(self, action: int) -> Tuple[List[List[int]], int, bool, dict]:
        """
        Steps through the game by doing one action for the player and one for the enemies.
        Starts by calculating fov to see if any enemies see agent.

        Args:
            action (int): The discrete action chose by the agent from the action space.

        Returns:
            Tuple[List[List[int]], int, bool, dict]: A tuple consisting of the next state, reward, 
            if the episode is done, and an info dictionary
        """

        self.engine.fov()
        reward = 0
        action = action_translator[action]
        action_type, dest = self.engine.bump(self.engine.player.pos, action)
        
        # ****** Reward Functions: Feel free to uncomment out what you want to use (made hastily for deadline). ******
        
        # Rewards agent for walking towards the exit path, but removes that reward if agent walks away.
        """exit_path = get_path_to(self.engine.player, self.exit_location, self.engine.level)
        if (exit_path[1], exit_path[0]) == ((self.engine.player.pos[0] + action[0]), (self.engine.player.pos[1] + action[1])):
            reward += 5
            self.path_reward += 1
        else:
            if self.path_reward > 0:
                reward -= 5
                self.path_reward -= 1"""

        """if action_type == Attack and dest.is_dead():
            reward += 20
            self.enemies_killed += 1
        elif dest.char == "#":
            reward -= 1
        elif dest.char == "z":
            reward += 2
        elif dest.char == "v":
            reward += 3"""
        if dest.char == ">":
            self.exits_taken += 1
            reward += 150
        """elif dest.char == "+":
            reward += 3 * abs(self.last_hp - self.engine.player.hp)
            self.last_hp = copy.deepcopy(self.engine.player.hp)
            self.potions_taken += 1"""
            
        # ****** End of Main Reward Functions ******

        self.engine.handle_enemy_turns()
        
        if self.engine.player.is_dead():
            #reward -= 50
            self.done = True
            #print("Player is dead.")
            
        """elif self.last_hp < self.engine.player.hp:
            #reward -= 20 * (self.last_hp - self.engine.player.hp)
            self.last_hp = copy.deepcopy(self.engine.player.hp)"""
        
        if self.time_spent >= 250:
            #reward -= 75
            #print("Time over.")
            self.done = True
        
        self.time_spent += 1
        if self.to_image:
            next_state, info = self.translate_map_to_image()
        else:
            next_state, info = self.translate_map_to_numbers()
            
        # Rewarding agent for exploring
        reward += ceil(self.explored_reward/2)
        self.explored_reward = 0
        
        info["exits taken"] = self.exits_taken
        
        return next_state, reward, self.done, info

    def render(self, mode="human") -> None:
        raise NotImplementedError
    
    def reset(self) -> List[List[int]]:
        # Resets all necessary values.
        self.player = copy.deepcopy(player)
        self.engine = Engine(self.player, self.seed_num, self.fixed_seed)
        self.time_spent = 0
        self.path_reward = 0
        self.explored_reward = 0
        self.exits_taken = 0
        self.done = False
        if self.to_image:
            obs, info = self.translate_map_to_image()
        else:
            obs, info = self.translate_map_to_numbers()
        return obs