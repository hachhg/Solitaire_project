"""Peg-solitaire rules with no dependency on Tkinter or any user interface."""

from board import Board, Position


class PegSolitaireGame:
    """Keep board state, validate jumps, and determine the game's result."""

    # The homework overview permits both orthogonal and diagonal jumps.
    DIRECTIONS = tuple(
        (row, column)
        for row in (-1, 0, 1)
        for column in (-1, 0, 1)
        if (row, column) != (0, 0)
    )

    def __init__(self, size=7, board_type="English"):
        self.new_game(size, board_type)

    def new_game(self, size=7, board_type="English"):
        """Replace the game only after the supplied settings have been validated."""
        new_board = Board(size, board_type)
        new_holes = new_board.holes()
        self.board = new_board
        self.holes = new_holes
        self.pegs = set(new_holes) - {new_board.center}
        self.move_count = 0

    @property
    def peg_count(self):
        """Return the number of remaining pegs."""
        return len(self.pegs)

    def is_valid_move(self, start: Position, end: Position):
        """Check a two-position jump over exactly one adjacent peg."""
        if start not in self.pegs or end not in self.holes or end in self.pegs:
            return False
        delta = end[0] - start[0], end[1] - start[1]
        if delta not in {(2 * row, 2 * col) for row, col in self.DIRECTIONS}:
            return False
        jumped = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
        return jumped in self.pegs

    def legal_moves(self):
        """List available jumps in a stable order for testing and display."""
        moves = []
        for start in sorted(self.pegs):
            for row, column in self.DIRECTIONS:
                end = start[0] + 2 * row, start[1] + 2 * column
                if self.is_valid_move(start, end):
                    moves.append((start, end))
        return moves

    def move(self, start: Position, end: Position):
        """Apply a legal jump; reject an illegal jump without changing anything."""
        if not self.is_valid_move(start, end):
            return False
        jumped = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
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
        return {1: "Outstanding", 2: "Very Good", 3: "Good"}.get(
            self.peg_count, "Average"
        )
