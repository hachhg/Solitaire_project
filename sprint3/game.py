"""Peg solitaire rules for manual and automated games."""

import random

from .board import Board


class PegSolitaireGame:
    """Own the board state, jump rules, counters and result."""

    MODE = "Manual"
    DIRECTIONS = (
        (-2, -2), (-2, 0), (-2, 2),
        (0, -2),           (0, 2),
        (2, -2),  (2, 0),  (2, 2),
    )

    def __init__(self, size=7, board_type="English", seed=None):
        self._random = random.Random(seed)
        self.new_game(size, board_type)

    def new_game(self, size=7, board_type="English"):
        """Validate the settings before replacing the current game."""
        board = Board(size, board_type)
        self._board = board
        self._holes = frozenset(board.holes())
        self._pegs = set(self._holes)
        self._pegs.remove(board.center)
        self._move_count = 0

    @property
    def board(self):
        return self._board

    @property
    def holes(self):
        return self._holes

    @property
    def pegs(self):
        """Return a set that callers can read but cannot change."""
        return frozenset(self._pegs)

    @property
    def move_count(self):
        return self._move_count

    @property
    def peg_count(self):
        return len(self._pegs)

    def restore_position(self, positions, move_count=0):
        """Restore a recorded position after validating all supplied values."""
        if type(move_count) is not int or move_count < 0:
            raise ValueError("Move count must be a nonnegative whole number.")
        pegs = set()
        for position in positions:
            if not isinstance(position, (list, tuple)) or len(position) != 2:
                raise ValueError("A position must contain a row and column.")
            row, column = position
            if type(row) is not int or type(column) is not int:
                raise ValueError("Coordinates must be whole numbers.")
            position = (row, column)
            if position not in self.holes or position in pegs:
                raise ValueError("Peg positions must be unique holes on the board.")
            pegs.add(position)
        if not pegs:
            raise ValueError("A game must contain at least one peg.")
        self._pegs = pegs
        self._move_count = move_count

    def is_valid_move(self, start, end):
        """A jump goes two cells over one peg into an empty hole."""
        if start not in self.holes or end not in self.holes:
            return False
        if start not in self._pegs or end in self._pegs:
            return False
        row_change = end[0] - start[0]
        column_change = end[1] - start[1]
        if (row_change, column_change) not in self.DIRECTIONS:
            return False

        middle_row = (start[0] + end[0]) // 2
        middle_column = (start[1] + end[1]) // 2
        jumped_peg = (middle_row, middle_column)
        return jumped_peg in self._pegs

    def legal_moves(self):
        """Find every legal jump, in a stable order."""
        moves = []
        for start in sorted(self._pegs):
            for row_change, column_change in self.DIRECTIONS:
                end = (start[0] + row_change, start[1] + column_change)
                if self.is_valid_move(start, end):
                    moves.append((start, end))
        return moves

    def move(self, start, end):
        """Return False without changes, or apply one legal jump and return True."""
        if not self.is_valid_move(start, end):
            return False
        middle_row = (start[0] + end[0]) // 2
        middle_column = (start[1] + end[1]) // 2
        jumped_peg = (middle_row, middle_column)

        self._pegs.remove(start)
        self._pegs.remove(jumped_peg)
        self._pegs.add(end)
        self._move_count += 1
        return True

    def is_game_over(self):
        if self.peg_count == 1:
            return True
        return len(self.legal_moves()) == 0

    def is_won(self):
        return self.peg_count == 1

    def rating(self):
        if not self.is_game_over():
            return None
        if self.peg_count == 1:
            return "Outstanding"
        if self.peg_count == 2:
            return "Very Good"
        if self.peg_count == 3:
            return "Good"
        return "Average"


class ManualGame(PegSolitaireGame):
    """The player chooses jumps and may rearrange the remaining pegs."""

    MODE = "Manual"

    def randomize(self):
        """Rearrange pegs without changing their count, board or move count."""
        if self.is_game_over():
            return False
        positions = self._random.sample(sorted(self.holes), self.peg_count)
        self.restore_position(positions, self.move_count)
        return True


class AutomatedGame(PegSolitaireGame):
    """Choose a legal jump at random, using the same rules as a human player."""

    MODE = "Automated"

    def auto_move(self):
        """Make one legal jump, or return None when no jumps remain."""
        moves = self.legal_moves()
        if not moves:
            return None
        start, end = self._random.choice(moves)
        self.move(start, end)
        return (start, end)


def create_game(size=7, board_type="English", mode="Manual", seed=None):
    """Create the selected game type in one place."""
    if mode == "Manual":
        return ManualGame(size, board_type, seed)
    if mode == "Automated":
        return AutomatedGame(size, board_type, seed)
    raise ValueError("Choose Manual or Automated mode.")
