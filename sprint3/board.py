"""Board settings and playable holes."""


class Board:
    """Build an English, Hexagon or Diamond board."""

    TYPES = ("English", "Hexagon", "Diamond")

    def __init__(self, size=7, board_type="English"):
        if type(size) is not int or size < 5 or size % 2 == 0:
            raise ValueError("Board size must be an odd whole number of at least 5.")
        if board_type not in self.TYPES:
            raise ValueError("Choose English, Hexagon, or Diamond.")
        self._size = size
        self._board_type = board_type

    def get_size(self):
        return self._size

    def get_board_type(self):
        return self._board_type

    def get_center(self):
        return (self.get_size() // 2, self.get_size() // 2)

    def holes(self):
        """Return the playable zero-based row and column pairs."""
        middle = self.get_size() // 2
        holes = set()
        for row in range(self.get_size()):
            for column in range(self.get_size()):
                if self.get_board_type() == "English":
                    middle_rows = abs(row - middle) <= 1
                    middle_columns = abs(column - middle) <= 1
                    valid = middle_rows or middle_columns
                elif self.get_board_type() == "Diamond":
                    distance = abs(row - middle) + abs(column - middle)
                    valid = distance <= middle
                else:
                    valid = abs(row - column) <= middle
                if valid:
                    holes.add((row, column))
        return holes
