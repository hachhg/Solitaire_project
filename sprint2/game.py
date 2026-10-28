"""Peg-solitaire rules with no dependency on Tkinter or any user interface."""

from .board import Board


class PegSolitaireGame:
    """Keep board state, validate jumps, and determine the game's result."""

    # Each jump moves two cells in one of these eight directions.
    DIRECTIONS = (
        (-2, -2), (-2, 0), (-2, 2),
        (0, -2),           (0, 2),
        (2, -2),  (2, 0),  (2, 2),
    )

    def __init__(self, size=7, board_type="English"):
        self.new_game(size, board_type)

    def new_game(self, size=7, board_type="English"):
        """Replace the game only after the supplied settings have been validated."""
        board = Board(size, board_type)
        holes = board.holes()

        self.board = board
        self.holes = holes
        self.pegs = holes - {board.center}
        self.move_count = 0

    @property
    def peg_count(self):
        """Return the number of remaining pegs."""
        return len(self.pegs)

    def is_valid_move(self, start, end):
        """Check a two-position jump over exactly one adjacent peg."""
        if start not in self.holes or end not in self.holes:
            return False
        if start not in self.pegs or end in self.pegs:
            return False

        row_change = end[0] - start[0]
        column_change = end[1] - start[1]
        if (row_change, column_change) not in self.DIRECTIONS:
            return False

        middle_row = (start[0] + end[0]) // 2
        middle_column = (start[1] + end[1]) // 2
        jumped = (middle_row, middle_column)
        return jumped in self.pegs

    def legal_moves(self):
        """List available jumps in a stable order for testing and display."""
        moves = []
        for start in sorted(self.pegs):
            for row_change, column_change in self.DIRECTIONS:
                end = (start[0] + row_change, start[1] + column_change)
                if self.is_valid_move(start, end):
                    moves.append((start, end))
        return moves

    def move(self, start, end):
        """Apply a legal jump; reject an illegal jump without changing anything."""
        if not self.is_valid_move(start, end):
            return False
        middle_row = (start[0] + end[0]) // 2
        middle_column = (start[1] + end[1]) // 2
        jumped = (middle_row, middle_column)
        self.pegs.remove(start)
        self.pegs.remove(jumped)
        self.pegs.add(end)
        self.move_count += 1
        return True

    def is_game_over(self):
        """A game ends when one peg remains or no legal jumps remain."""
        return self.peg_count <= 1 or not self.legal_moves()

    def is_won(self):
        """A single remaining peg wins, regardless of its location."""
        return self.peg_count == 1

    def rating(self):
        """Return a final rating, or None while the game can still continue."""
        if not self.is_game_over():
            return None
        if self.peg_count == 1:
            return "Outstanding"
        if self.peg_count == 2:
            return "Very Good"
        if self.peg_count == 3:
            return "Good"
        return "Average"
