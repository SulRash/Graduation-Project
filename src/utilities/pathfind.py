from __future__ import annotations

import numpy as np

from typing import List, TYPE_CHECKING, Tuple

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

from src.entities.entity import Actor, Item

if TYPE_CHECKING:
    from src.world.level import Level

def get_cost(level: Level) -> List[List[int]]:
    """
    Calculates cost of each tile on the level to give a general sense
    of cost around the stage for pathfinding.
    
    Args:
        level (Level): Passed through to get information on tiles.

    Returns:
        List[List[int]]: A 2D array of integers representing the map
    """
    cost = np.array([[0]*level.height]*level.width)
    for y in range(level.height):
        for x in range(level.width):
            if level.tiles[x,y].char == ">" or level.tiles[x,y].char == "+":
                cost[x,y] = 8
            elif isinstance(level.tiles[x,y], Actor):
                cost[x,y] = 5
            elif level.tiles[x,y].blocks_movement:
                continue
            else:
                cost[x,y] = 1
    return cost
    
def get_path_to(entity: Actor, goal: Actor or Item, level: Level) -> Tuple[int, int]:
    """
    Gets path from any actor to another entity. Uses the astar algorithm.

    Args:
        entity (Actor): The entity searching for the goal.
        goal (Actor or Item): The goal object.
        level (Level): The level to get the tiles.

    Returns:
        Tuple[int, int]: Returns the next coordinate to go to.
    """
    cost = get_cost(level)
    grid = Grid(matrix=cost)
        
    start = grid.node(entity.pos[1], entity.pos[0])
    end = grid.node(goal[1], goal[0])
    
    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
    
    path, runs = finder.find_path(start, end, grid)
    try:
        return path[1]
    except IndexError:
        return (0,0)