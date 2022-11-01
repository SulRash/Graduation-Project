from __future__ import annotations

import numpy as np
from typing import Tuple, TYPE_CHECKING

class Entity():

    def __init__(self, name: str, char: str, blocks_movement: bool):
        self.name = name
        self.char = char
        self.blocks_movement = blocks_movement
    
    @property
    def pos(self) -> Tuple[int, int]:
        return self.x, self.y
        
    def set_pos(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Actor(Entity):

    def __init__(self, name: str, char: str, blocks_movement: bool, hp: int):
        super().__init__(name, char, blocks_movement)
        self.hp = hp
        self.max_hp = hp
  
    def damage(self, change: int) -> None:
        change -= self.defense
        self.hp -= max(change, 0)
        if self.hp <= 0:
            self.die()

    def die(self) -> None:
        #print(f"{self.name} has suffered fatal wounds.")
        return
        
    def is_dead(self) -> bool:
        if self.hp > 0:
            return False
        else:
            return True

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy
        
class Fighter(Actor):
    def __init__(self, name: str, char: str, blocks_movement: bool, hp: int, attack: int, defense: int):
        super().__init__(name, char, blocks_movement, hp)
        self.attack = attack
        self.defense = defense
        self.gold = 0
        
class AIFighter(Actor):
    def __init__(self, name: str, char: str, blocks_movement: bool, hp: int, attack: int, defense: int):
        super().__init__(name, char, blocks_movement, hp)
        self.attack = attack
        self.defense = defense

class Item(Entity):
    def __init__(self, name: str, char: str, blocks_movement: bool = False):
        super().__init__(name, char, blocks_movement)
        self.explored = False
        
    def perform(self):
        raise NotImplemented

class Potion(Item):
    def __init__(self, name: str, char: str, blocks_movement: bool = False, hp: int = 0, attack: int = 0, defense: int = 0):
        super().__init__(name, char, blocks_movement)
        self.hp = hp
        self.attack = attack
        self.defense = defense
    
    def perform(self, engine):
        engine.player.hp += min(engine.player.max_hp - engine.player.hp, self.hp)
        engine.player.attack += self.attack
        engine.player.defense += self.defense

class Exit(Item):
    def __init__(self, name: str, char: str, blocks_movement: bool = False):
        super().__init__(name, char, blocks_movement)
    
    def perform(self, engine):
        engine.next_level()