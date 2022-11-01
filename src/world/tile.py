class Tile:

    def __init__(self, blocks_movement: bool, see_through: bool, char: str, dark: str, explored: bool, already_explored: bool = False) -> None:
        """
        Tile class for walls and floors. Could be extendable to other types too.

        Args:
            blocks_movement (bool): If tile blocks movement for entities.
            see_through (bool): If entities can see through the tile.
            char (str): How it is rendered in default view
            dark (str): [In-Progress] To be used to rendering a different view.
            explored (bool): If tile is explored by player.
        """
        self.dark = dark
        self.char = char
        self.see_through = see_through
        self.blocks_movement = blocks_movement
        self.explored = explored
        self.already_explored = already_explored

floor = Tile(
    blocks_movement=False,
    see_through=True,
    dark="▩",
    char=".",
    explored=False
)

wall = Tile(
    blocks_movement=True,
    see_through=False,
    dark="■",
    char="#",
    explored=False,
)

tunnel = Tile(
    blocks_movement=False,
    see_through=True,
    dark="▩",
    char="-",
    explored=False
)
