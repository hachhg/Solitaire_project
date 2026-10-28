"""Acceptance tests for the board shapes and peg-solitaire game rules."""

import unittest

from board import Board
from game import PegSolitaireGame


class BoardTests(unittest.TestCase):
    """Check sizes, defaults and the three independent board shapes."""

    def test_default_settings(self):
        board = Board()
        self.assertEqual((board.size, board.board_type), (7, "English"))

    def test_all_types_accept_valid_odd_sizes(self):
        for size in (5, 7, 9, 11):
            for board_type in Board.TYPES:
                with self.subTest(size=size, board_type=board_type):
                    board = Board(size, board_type)
                    self.assertIn(board.center, board.holes())
                    self.assertTrue(all(0 <= r < size and 0 <= c < size
                                        for r, c in board.holes()))

    def test_invalid_sizes_are_rejected(self):
        for size in (0, -5, 3, 4, 6, "7", 7.0, True):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    Board(size)

    def test_invalid_type_is_rejected(self):
        with self.assertRaises(ValueError):
            Board(7, "Triangle")

    def test_english_shape_has_33_holes(self):
        holes = Board(7, "English").holes()
        expected = {(r, c) for r in range(7) for c in range(7)
                    if r in (2, 3, 4) or c in (2, 3, 4)}
        self.assertEqual(holes, expected)
        self.assertEqual(len(holes), 33)

    def test_hexagon_shape_has_37_holes(self):
        holes = Board(7, "Hexagon").holes()
        self.assertEqual(len(holes), 37)
        self.assertEqual([sum(r == row for r, c in holes) for row in range(7)],
                         [4, 5, 6, 7, 6, 5, 4])
        self.assertNotIn((0, 6), holes)
        self.assertNotIn((6, 0), holes)
        self.assertIn((0, 0), holes)
        self.assertIn((6, 6), holes)

    def test_diamond_shape_has_25_holes(self):
        holes = Board(7, "Diamond").holes()
        self.assertEqual(len(holes), 25)
        self.assertEqual([sum(r == row for r, c in holes) for row in range(7)],
                         [1, 3, 5, 7, 5, 3, 1])
        self.assertIn((0, 3), holes)
        self.assertNotIn((0, 2), holes)


class GameTests(unittest.TestCase):
    """Verify each new-game, movement and end-of-game acceptance criterion."""

    def test_initial_center_is_only_empty_hole(self):
        for size in (5, 7, 9):
            for board_type in Board.TYPES:
                with self.subTest(size=size, board_type=board_type):
                    game = PegSolitaireGame(size, board_type)
                    self.assertEqual(game.holes - game.pegs, {game.board.center})
                    self.assertEqual(game.peg_count, len(game.holes) - 1)
                    self.assertEqual(game.move_count, 0)

    def test_restart_restores_initial_board(self):
        game = PegSolitaireGame()
        game.move((1, 3), (3, 3))
        game.new_game(7, "English")
        self.assertEqual(game.pegs, game.holes - {(3, 3)})
        self.assertEqual(game.move_count, 0)

    def test_new_game_changes_size_and_type(self):
        game = PegSolitaireGame()
        game.new_game(9, "Diamond")
        self.assertEqual((game.board.size, game.board.board_type), (9, "Diamond"))
        self.assertEqual(game.peg_count, 40)

    def test_invalid_new_game_preserves_existing_game(self):
        game = PegSolitaireGame()
        game.move((1, 3), (3, 3))
        before = (game.board, game.pegs.copy(), game.move_count)
        for size, board_type in ((6, "English"), (7, "Triangle")):
            with self.subTest(size=size, board_type=board_type):
                with self.assertRaises(ValueError):
                    game.new_game(size, board_type)
                self.assertEqual((game.board, game.pegs, game.move_count), before)

    def test_valid_jump_updates_all_three_holes(self):
        """AI-generated test 1: inspect the full state change, not just True."""
        game = PegSolitaireGame()
        self.assertTrue(game.move((1, 3), (3, 3)))
        self.assertNotIn((1, 3), game.pegs)
        self.assertNotIn((2, 3), game.pegs)
        self.assertIn((3, 3), game.pegs)
        self.assertEqual(game.peg_count, 31)

    def test_invalid_jump_leaves_board_unchanged(self):
        """AI-generated test 2: reject a move without changing any game state."""
        game = PegSolitaireGame()
        before = game.pegs.copy()
        self.assertFalse(game.move((0, 2), (3, 3)))
        self.assertEqual(game.pegs, before)
        self.assertEqual(game.move_count, 0)

    def test_jumps_in_all_eight_directions(self):
        # Use a large diamond so all tested endpoints are playable holes.
        for dr, dc in ((-1, -1), (-1, 0), (-1, 1), (0, -1),
                       (0, 1), (1, -1), (1, 0), (1, 1)):
            with self.subTest(direction=(dr, dc)):
                game = PegSolitaireGame(9, "Diamond")
                start = (4, 4)
                middle = (4 + dr, 4 + dc)
                end = (4 + 2 * dr, 4 + 2 * dc)
                game.pegs = {start, middle}
                self.assertTrue(game.move(start, end))
                self.assertEqual(game.pegs, {end})

    def test_diagonal_jump_is_legal(self):
        game = PegSolitaireGame()
        game.pegs = {(2, 2), (3, 3)}
        self.assertTrue(game.move((2, 2), (4, 4)))
        self.assertEqual(game.pegs, {(4, 4)})

    def test_occupied_destination_is_rejected(self):
        game = PegSolitaireGame()
        before = game.pegs.copy()
        self.assertFalse(game.move((0, 2), (2, 2)))
        self.assertEqual(game.pegs, before)

    def test_missing_jumped_peg_is_rejected(self):
        game = PegSolitaireGame()
        game.pegs = {(1, 3), (6, 3)}
        before = game.pegs.copy()
        self.assertFalse(game.move((1, 3), (3, 3)))
        self.assertEqual(game.pegs, before)

    def test_off_board_destination_is_rejected(self):
        game = PegSolitaireGame()
        for end in ((-1, 2), (0, 0), (7, 2)):
            with self.subTest(end=end):
                before = game.pegs.copy()
                self.assertFalse(game.move((1, 2), end))
                self.assertEqual(game.pegs, before)

    def test_empty_source_is_rejected(self):
        game = PegSolitaireGame()
        before = game.pegs.copy()
        self.assertFalse(game.move((3, 3), (3, 1)))
        self.assertEqual(game.pegs, before)

    def test_initial_english_board_has_four_moves(self):
        game = PegSolitaireGame()
        self.assertEqual(set(game.legal_moves()), {
            ((1, 3), (3, 3)), ((3, 1), (3, 3)),
            ((3, 5), (3, 3)), ((5, 3), (3, 3)),
        })

    def test_last_jump_wins_the_game(self):
        game = PegSolitaireGame()
        game.pegs = {(3, 1), (3, 2)}
        self.assertTrue(game.move((3, 1), (3, 3)))
        self.assertTrue(game.is_game_over())
        self.assertTrue(game.is_won())
        self.assertEqual(game.rating(), "Outstanding")

    def test_last_jump_can_end_without_a_win(self):
        game = PegSolitaireGame()
        game.pegs = {(3, 1), (3, 2), (0, 2)}
        self.assertTrue(game.move((3, 1), (3, 3)))
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.is_won())
        self.assertEqual(game.peg_count, 2)
        self.assertEqual(game.rating(), "Very Good")

    def test_game_continues_when_jumps_remain(self):
        game = PegSolitaireGame()
        game.move((1, 3), (3, 3))
        self.assertFalse(game.is_game_over())
        self.assertFalse(game.is_won())
        self.assertTrue(game.legal_moves())
        self.assertIsNone(game.rating())

    def test_moves_after_game_over_do_not_change_state(self):
        for pegs in ({(3, 3)}, {(0, 2), (6, 4)}):
            with self.subTest(pegs=pegs):
                game = PegSolitaireGame()
                game.pegs = pegs.copy()
                self.assertTrue(game.is_game_over())
                self.assertFalse(game.move((0, 2), (2, 2)))
                self.assertEqual(game.pegs, pegs)

    def test_ratings_depend_on_final_peg_count(self):
        for pegs, expected in (({(3, 3)}, "Outstanding"),
                               ({(0, 2), (6, 4)}, "Very Good"),
                               ({(0, 2), (6, 4), (3, 0)}, "Good"),
                               ({(0, 2), (6, 4), (3, 0), (3, 6)}, "Average")):
            with self.subTest(rating=expected):
                game = PegSolitaireGame()
                game.pegs = pegs
                self.assertEqual(game.rating(), expected)


if __name__ == "__main__":
    unittest.main()
