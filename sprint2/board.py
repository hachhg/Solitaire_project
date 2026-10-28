"""Build the valid holes for the three peg-solitaire board shapes."""

from dataclasses import dataclass


Position = tuple[int, int]


@dataclass(frozen=True)
class Board:
    """Describe a board independently of its pegs or graphical display.

    Size is the width and height of the enclosing square grid. Coordinates
    are zero-based (row, column). English uses a central band three holes
    wide; Diamond uses Manhattan distance; Hexagon trims two opposite corners.
    """

    size: int = 7
    board_type: str = "English"

    TYPES = ("English", "Hexagon", "Diamond")

    def __post_init__(self):
        """Reject unsupported sizes and board types before building a game."""
        if type(self.size) is not int or self.size < 5 or self.size % 2 == 0:
            raise ValueError("Board size must be an odd whole number of at least 5.")
        if self.board_type not in self.TYPES:
            raise ValueError("Choose English, Hexagon, or Diamond.")

    @property
    def center(self) -> Position:
        """Return the hole left empty at the start of a new game."""
        return self.size // 2, self.size // 2

    def holes(self) -> frozenset[Position]:
        """Return every playable hole, excluding the corners outside the shape."""
        middle = self.size // 2
        result = set()
        for row in range(self.size):
            for column in range(self.size):
                if self.board_type == "English":
                    valid = abs(row - middle) <= 1 or abs(column - middle) <= 1
                elif self.board_type == "Diamond":
                    valid = abs(row - middle) + abs(column - middle) <= middle
                else:
                    valid = abs(row - column) <= middle
                if valid:
                    result.add((row, column))
        return frozenset(result)
