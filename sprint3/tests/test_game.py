"""Test the shared rules, manual play, automated play and randomization."""

import unittest

from sprint3.board import Board
from sprint3.game import AutomatedGame, ManualGame, PegSolitaireGame, create_game


class BoardTests(unittest.TestCase):
    def test_board_types_and_sizes(self):
        expected = {"English": 33, "Hexagon": 37, "Diamond": 25}
        for name, count in expected.items():
            with self.subTest(board=name):
                board = Board(7, name)
                self.assertEqual(len(board.holes()), count)
                self.assertIn(board.center, board.holes())
                self.assertEqual(Board(5, name).size, 5)

    def test_english_board_is_a_plus_sign(self):
        holes = Board(7, "English").holes()
        expected = {(r, c) for r in range(7) for c in range(7)
                    if r in (2, 3, 4) or c in (2, 3, 4)}
        self.assertEqual(holes, expected)

    def test_invalid_settings_are_rejected(self):
        for size in (3, 6, True, "7"):
            with self.subTest(size=size), self.assertRaises(ValueError):
                Board(size)
        with self.assertRaises(ValueError):
            Board(7, "Triangle")


class ManualGameTests(unittest.TestCase):
    def test_new_game_uses_settings_and_resets_counts(self):
        game = ManualGame()
        game.move((1, 3), (3, 3))
        game.new_game(5, "Hexagon")
        self.assertEqual((game.board.size, game.board.board_type), (5, "Hexagon"))
        self.assertEqual(game.pegs, game.holes - {game.board.center})
        self.assertEqual(game.move_count, 0)

    def test_valid_jump_updates_three_holes(self):
        game = ManualGame(7, "English")
        self.assertTrue(game.move((1, 3), (3, 3)))
        self.assertNotIn((1, 3), game.pegs)
        self.assertNotIn((2, 3), game.pegs)
        self.assertIn((3, 3), game.pegs)
        self.assertEqual((game.peg_count, game.move_count), (31, 1))

    def test_invalid_jump_leaves_state_unchanged(self):
        game = ManualGame()
        before = (game.pegs, game.move_count)
        self.assertFalse(game.move((0, 2), (3, 3)))
        self.assertEqual((game.pegs, game.move_count), before)

    def test_jumps_in_all_eight_directions(self):
        for dr, dc in PegSolitaireGame.DIRECTIONS:
            with self.subTest(direction=(dr, dc)):
                game = ManualGame(9, "Diamond")
                start = (4, 4)
                middle = (4 + dr // 2, 4 + dc // 2)
                end = (4 + dr, 4 + dc)
                game.restore_position([start, middle])
                self.assertTrue(game.move(start, end))
                self.assertEqual(game.pegs, {end})

    def test_winning_move_ends_game(self):
        game = ManualGame()
        game.restore_position([(3, 1), (3, 2)])
        self.assertTrue(game.move((3, 1), (3, 3)))
        self.assertTrue(game.is_game_over())
        self.assertTrue(game.is_won())
        self.assertEqual(game.rating(), "Outstanding")

    def test_no_legal_moves_ends_game(self):
        game = ManualGame()
        game.restore_position([(0, 2), (6, 4)])
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.is_won())
        self.assertEqual(game.rating(), "Very Good")

    def test_invalid_new_game_preserves_current_state(self):
        game = ManualGame()
        before = (game.board, game.pegs, game.move_count)
        with self.assertRaises(ValueError):
            game.new_game(6)
        self.assertEqual((game.board, game.pegs, game.move_count), before)

    def test_pegs_and_counts_cannot_be_assigned_by_clients(self):
        game = ManualGame()
        with self.assertRaises(AttributeError):
            game.pegs.add((3, 3))
        with self.assertRaises(AttributeError):
            game.pegs = set()
        with self.assertRaises(AttributeError):
            game.move_count = 10

    def test_restore_rejects_bad_positions_without_changes(self):
        game = ManualGame()
        before = (game.pegs, game.move_count)
        for positions, moves in (([], 0), ([(0, 0)], 0),
                                 ([(3, 3), (3, 3)], 0), ([(3, 3)], -1)):
            with self.subTest(positions=positions), self.assertRaises(ValueError):
                game.restore_position(positions, moves)
            self.assertEqual((game.pegs, game.move_count), before)


class RandomizationTests(unittest.TestCase):
    def test_randomization_preserves_counts_and_board(self):
        game = ManualGame(seed=12)
        game.move((1, 3), (3, 3))
        before = (game.board, game.peg_count, game.move_count)
        positions = game.pegs
        self.assertTrue(game.randomize())
        self.assertEqual((game.board, game.peg_count, game.move_count), before)
        self.assertTrue(game.pegs <= game.holes)
        self.assertNotEqual(game.pegs, positions)

    def test_randomization_can_be_repeated_during_manual_play(self):
        game = ManualGame(5, "English", seed=7)
        for _ in range(3):
            start, end = game.legal_moves()[0]
            game.move(start, end)
            count = game.peg_count
            self.assertTrue(game.randomize())
            self.assertEqual(game.peg_count, count)

    def test_finished_game_cannot_be_randomized(self):
        game = ManualGame()
        game.restore_position([(3, 3)])
        self.assertFalse(game.randomize())
        self.assertEqual(game.pegs, {(3, 3)})


class AutomatedGameTests(unittest.TestCase):
    def test_factory_selects_manual_or_automated(self):
        self.assertIsInstance(create_game(mode="Manual"), ManualGame)
        self.assertIsInstance(create_game(mode="Automated"), AutomatedGame)
        with self.assertRaises(ValueError):
            create_game(mode="Other")

    def test_automated_move_is_legal_and_removes_one_peg(self):
        game = AutomatedGame(seed=3)
        legal = game.legal_moves()
        before = game.pegs
        move = game.auto_move()
        self.assertIn(move, legal)
        start, end = move
        middle = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        self.assertEqual(game.pegs, (before - {start, middle}) | {end})
        self.assertEqual(game.move_count, 1)

    def test_automated_games_finish_on_all_board_types(self):
        for name in Board.TYPES:
            for size in (5, 7):
                with self.subTest(board=name, size=size):
                    game = AutomatedGame(size, name, seed=10)
                    initial_count = game.peg_count
                    for _ in range(initial_count):
                        if game.auto_move() is None:
                            break
                    self.assertTrue(game.is_game_over())
                    self.assertEqual(game.legal_moves(), [])
                    self.assertEqual(game.peg_count + game.move_count, initial_count)
                    self.assertIsNotNone(game.rating())

    def test_automated_move_after_game_over_changes_nothing(self):
        game = AutomatedGame()
        game.restore_position([(3, 3)], 5)
        self.assertIsNone(game.auto_move())
        self.assertEqual((game.pegs, game.move_count), ({(3, 3)}, 5))


if __name__ == "__main__":
    unittest.main()
