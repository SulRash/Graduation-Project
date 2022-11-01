import copy
from src.entities.entity import Entity, Fighter, AIFighter, Potion, Exit

# Corpse
corpse = Entity(name="corpse", char="q", blocks_movement=False)

# Player
player = Fighter(name="player", char="@", blocks_movement=True, hp=20, attack=5, defense=2)

# Enemies
zombie = AIFighter(name="zombie", char="z", blocks_movement=True, hp=8, attack=3, defense=1)
vampire = AIFighter(name="vampire", char="v", blocks_movement=True, hp=12, attack=4, defense=1)

# Items
exit = Exit(name="exit", char=">", blocks_movement=False)
health_potion = Potion(name="health potion", char="+", blocks_movement=False, hp=10)