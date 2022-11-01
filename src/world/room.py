from __future__ import annotations

from typing import Tuple

class RectangleRoom:

    def __init__(self, x1: int, y1: int, width: int, height: int) -> None:
        """
        Rectangle room class for handling some necessary functions for room generation during level creation.

        Args:
            x1 (int): Bottom left corner x coordinate.
            y1 (int): Bottom left corner y coordinate.
            width (int): Width of the rectangle.
            height (int): Height of the rectangle.
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + width
        self.y2 = y1 + height

    @property
    def space(self) -> Tuple[slice, slice]:
        """
        Calculates slices for getting the inner space of a room from the map.

        Returns:
            Tuple[slice, slice]: A tuple of slices for the x and y coordinates.
        """
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)
    
    @property
    def center(self) -> Tuple[int, int]:
        """
        Gets center of the room.

        Returns:
            Tuple[int, int]: A tuple of x and y coordinates
        """
        return int((self.x1 + self.x2) / 2), int((self.y1 + self.y2) / 2)
        
    
    def intersect(self, checked_room: RectangleRoom) -> bool:
        """
        Checks if this room intersects with another room.space

        Args:
            checked_room (RectangleRoom): The rectangle room to be checked against.

        Returns:
            bool: True if intersects, false otherwise.
        """
        return (
            self.x1 <= checked_room.x2
            and self.x2 >= checked_room.x1
            and self.y1 <= checked_room.y2
            and self.y2 >= checked_room.y1
        )