"""Create the holes for each peg-solitaire board shape."""


class Board:
    """Store a board's size, type and center position."""

    TYPES = ("English", "Hexagon", "Diamond")

    def __init__(self, size=7, board_type="English"):
        if type(size) is not int or size < 5 or size % 2 == 0:
            raise ValueError("Board size must be an odd whole number of at least 5.")
        if board_type not in self.TYPES:
            raise ValueError("Choose English, Hexagon, or Diamond.")

        self.size = size
        self.board_type = board_type
        self.center = (size // 2, size // 2)

    def holes(self):
        """Return a set of playable (row, column) positions."""
        middle = self.size // 2
        holes = set()

        for row in range(self.size):
            for column in range(self.size):
                if self.board_type == "English":
                    middle_rows = abs(row - middle) <= 1
                    middle_columns = abs(column - middle) <= 1
                    valid = middle_rows or middle_columns
                elif self.board_type == "Diamond":
                    distance = abs(row - middle) + abs(column - middle)
                    valid = distance <= middle
                else:
                    # Remove the upper-right and lower-left corners.
                    valid = abs(row - column) <= middle

                if valid:
                    holes.add((row, column))

        return holes
