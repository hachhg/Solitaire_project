"""Tkinter integration tests for the real GUI controls and event handlers.

Run on a computer with Tkinter and a graphical desktop. The test windows stay
withdrawn. Game-rule tests in test_game.py do not need a desktop.
"""

import tkinter as tk
import unittest
from types import SimpleNamespace

from solitaire_gui import SolitaireApp


class GuiTests(unittest.TestCase):
    """Check how the GUI applies settings and presents the model's results."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = SolitaireApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_default_controls(self):
        self.assertEqual(self.app.size_var.get(), "7")
        self.assertEqual(self.app.type_var.get(), "English")

    def test_changing_controls_waits_for_new_game(self):
        before = self.app.game.pegs.copy()
        self.app.size_var.set("9")
        self.app.type_var.set("Diamond")
        self.assertEqual(self.app.game.pegs, before)
        self.assertEqual(self.app.game.board.board_type, "English")
        self.app.new_game_button.invoke()
        self.assertEqual(self.app.game.board.size, 9)
        self.assertEqual(self.app.game.board.board_type, "Diamond")

    def test_invalid_size_shows_error_and_preserves_game(self):
        for value in ("6", "3", "abc", "7.5", ""):
            with self.subTest(value=value):
                before = self.app.game.pegs.copy()
                self.app.size_var.set(value)
                self.assertFalse(self.app.start_new_game())
                self.assertEqual(self.app.game.pegs, before)
                self.assertEqual(self.app.size_var.get(), "7")
                self.assertIn("Invalid settings", self.app.status_var.get())

    def test_two_canvas_clicks_make_a_move(self):
        self.app.draw_board()
        for position in ((1, 3), (3, 3)):
            x, y = self.app.centers[position]
            self.app.on_canvas_click(SimpleNamespace(x=x, y=y))
        self.assertEqual(self.app.game.peg_count, 31)
        self.assertEqual(self.app.game.move_count, 1)
        self.assertIsNone(self.app.selected)

    def test_illegal_destination_shows_error(self):
        before = self.app.game.pegs.copy()
        self.app.select_hole((0, 2))
        self.app.select_hole((3, 3))
        self.assertEqual(self.app.game.pegs, before)
        self.assertIn("Invalid move", self.app.status_var.get())

    def test_new_game_clears_selection_and_moves(self):
        self.app.select_hole((1, 3))
        self.app.select_hole((3, 3))
        self.app.select_hole((2, 2))
        self.app.start_new_game()
        self.assertEqual(self.app.game.peg_count, 32)
        self.assertEqual(self.app.game.move_count, 0)
        self.assertIsNone(self.app.selected)

    def test_win_message_and_moves_blocked(self):
        self.app.game.pegs = {(3, 1), (3, 2)}
        self.app.select_hole((3, 1))
        self.app.select_hole((3, 3))
        self.assertIn("You won!", self.app.status_var.get())
        self.assertIn("Outstanding", self.app.status_var.get())
        self.app.select_hole((3, 3))
        self.assertEqual(self.app.game.pegs, {(3, 3)})

    def test_no_moves_message_and_rating(self):
        self.app.game.pegs = {(3, 1), (3, 2), (0, 2)}
        self.app.select_hole((3, 1))
        self.app.select_hole((3, 3))
        self.assertIn("Game over", self.app.status_var.get())
        self.assertIn("Very Good", self.app.status_var.get())


if __name__ == "__main__":
    unittest.main()
