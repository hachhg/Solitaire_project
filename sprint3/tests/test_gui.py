"""Test real Tkinter handlers with hidden windows and mocked file dialogs."""

import json
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from sprint3.game import AutomatedGame
from sprint3.recording import GameRecording
from sprint3.solitaire_gui import SolitaireApp


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = SolitaireApp(self.root)
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "game.json"
        # Test one tick at a time without waiting for real wall-clock timers.
        self.after = patch.object(self.root, "after", return_value="test-timer").start()
        self.cancel = patch.object(self.root, "after_cancel").start()
        self.addCleanup(patch.stopall)

    def tearDown(self):
        self.root.destroy()

    def test_default_controls_show_manual_english_game(self):
        self.assertEqual(self.app.type_var.get(), "English")
        self.assertEqual(self.app.mode_var.get(), "Manual")
        self.assertEqual(self.app.game.get_peg_count(), 32)
        self.assertEqual(str(self.app.auto_button["state"]), "disabled")

    def test_selected_size_type_and_mode_apply_on_new_game(self):
        self.app.size_var.set("5")
        self.app.type_var.set("Hexagon")
        self.app.mode_var.set("Automated")
        self.assertEqual(self.app.game.MODE, "Manual")
        self.app.new_game_button.invoke()
        self.assertIsInstance(self.app.game, AutomatedGame)
        self.assertEqual((self.app.game.get_board().get_size(), self.app.game.get_board().get_board_type()), (5, "Hexagon"))
        self.assertEqual(self.app.game.get_move_count(), 0)
        self.assertEqual(str(self.app.random_button["state"]), "disabled")

    def test_invalid_settings_preserve_current_game(self):
        before = self.app.game
        self.app.size_var.set("6")
        self.assertFalse(self.app.start_new_game())
        self.assertIs(self.app.game, before)
        self.assertIn("Invalid settings", self.app.status_var.get())

    def test_manual_canvas_clicks_make_one_jump(self):
        self.app.draw_board()
        for position in ((1, 3), (3, 3)):
            x, y = self.app.centers[position]
            self.app.on_canvas_click(SimpleNamespace(x=x, y=y))
        self.assertEqual((self.app.game.get_peg_count(), self.app.game.get_move_count()), (31, 1))

    def test_invalid_manual_move_shows_error_without_changes(self):
        before = self.app.game.get_pegs()
        self.app.select_hole((0, 2))
        self.app.select_hole((3, 3))
        self.assertEqual(self.app.game.get_pegs(), before)
        self.assertEqual(self.app.game.get_move_count(), 0)
        self.assertIn("Invalid move", self.app.status_var.get())

    def test_manual_game_over_displays_result_and_rating(self):
        cases = [([(3, 1), (3, 2)], "You won!", "Outstanding"),
                 ([(3, 1), (3, 2), (0, 2)], "Game over", "Very Good")]
        for positions, message, rating in cases:
            with self.subTest(result=message):
                self.app.start_new_game()
                self.app.game.restore_position(positions)
                self.app.select_hole((3, 1))
                self.app.select_hole((3, 3))
                self.assertTrue(self.app.game.is_game_over())
                self.assertIn(message, self.app.status_var.get())
                self.assertIn(rating, self.app.status_var.get())
                self.assertEqual(str(self.app.random_button["state"]), "disabled")

    def test_automated_mode_blocks_manual_clicks(self):
        self.app.mode_var.set("Automated")
        self.app.start_new_game()
        before = self.app.game.get_pegs()
        self.app.select_hole((1, 3))
        self.app.select_hole((3, 3))
        self.assertEqual(self.app.game.get_pegs(), before)
        self.assertEqual(self.app.game.get_move_count(), 0)

    def test_autoplay_stops_at_game_over(self):
        self.app.mode_var.set("Automated")
        self.app.size_var.set("5")
        self.app.start_new_game()
        self.app.toggle_autoplay()
        for _ in range(21):
            if not self.app.running:
                break
            self.app.tick()
        self.assertTrue(self.app.game.is_game_over())
        self.assertFalse(self.app.running)
        self.assertIsNone(self.app._timer_id)
        self.assertIn("Rating:", self.app.status_var.get())

    def test_pause_and_new_game_cancel_pending_tick(self):
        self.app.mode_var.set("Automated")
        self.app.start_new_game()
        self.app.toggle_autoplay()
        self.app.toggle_autoplay()
        self.assertFalse(self.app.running)
        self.cancel.assert_called_with("test-timer")
        self.app.toggle_autoplay()
        self.app.start_new_game()
        self.assertFalse(self.app.running)
        self.assertEqual(self.app.game.get_move_count(), 0)

    def test_hint_does_not_make_a_move(self):
        before = self.app.game.get_pegs()
        self.app.hint_button.invoke()
        self.assertIn("Hint: click row", self.app.status_var.get())
        self.assertEqual(self.app.game.get_pegs(), before)
        self.assertEqual(self.app.game.get_move_count(), 0)

    def test_randomize_clears_selection_and_keeps_counts(self):
        self.app.select_hole((1, 3))
        self.assertTrue(self.app.randomize_board())
        self.assertIsNone(self.app.selected)
        self.assertEqual((self.app.game.get_peg_count(), self.app.game.get_move_count()), (32, 0))

    def test_recording_saves_only_successful_actions(self):
        with patch("sprint3.solitaire_gui.filedialog.asksaveasfilename", return_value=str(self.path)):
            self.app.record_var.set(True)
            self.app.change_recording()
        self.app.select_hole((0, 2))
        self.app.select_hole((3, 3))
        self.assertEqual(json.loads(self.path.read_text())["events"], [])
        self.app.selected = None
        self.app.select_hole((1, 3))
        self.app.select_hole((3, 3))
        self.app.randomize_board()
        events = json.loads(self.path.read_text())["events"]
        self.assertEqual([event["action"] for event in events], ["move", "randomize"])

    def test_cancel_recording_dialog_keeps_recording_off(self):
        with patch("sprint3.solitaire_gui.filedialog.asksaveasfilename", return_value=""):
            self.app.record_var.set(True)
            self.app.change_recording()
        self.assertFalse(self.app.record_var.get())
        self.assertIsNone(self.app.recording)

    def test_replay_displays_saved_final_position(self):
        recording = GameRecording(self.app.game)
        self.app.game.move((1, 3), (3, 3))
        recording.record_move((1, 3), (3, 3))
        recording.save(self.path)
        expected = self.app.game.get_pegs()
        with patch("sprint3.solitaire_gui.filedialog.askopenfilename", return_value=str(self.path)):
            self.assertTrue(self.app.open_replay())
        self.assertEqual(self.app.game.get_move_count(), 0)
        self.app.tick()
        self.assertFalse(self.app.running)
        self.assertEqual(self.app.game.get_pegs(), expected)
        self.assertIn("Replay finished", self.app.status_var.get())
        self.assertEqual(str(self.app.record_check["state"]), "disabled")

    def test_bad_replay_file_does_not_replace_game(self):
        before = self.app.game
        self.path.write_text("not a recording", encoding="utf-8")
        with patch("sprint3.solitaire_gui.filedialog.askopenfilename", return_value=str(self.path)):
            self.assertFalse(self.app.open_replay())
        self.assertIs(self.app.game, before)
        self.assertIn("Could not open recording", self.app.status_var.get())

    def test_recording_save_error_keeps_game_playable(self):
        self.app.recording = GameRecording(self.app.game)
        self.app.recording_path = str(self.path / "missing.json")
        self.app.record_var.set(True)
        self.app.select_hole((1, 3))
        self.app.select_hole((3, 3))
        self.assertEqual(self.app.game.get_move_count(), 1)
        self.assertIn("could not be saved", self.app.status_var.get())
        self.assertFalse(self.app.record_var.get())


if __name__ == "__main__":
    unittest.main()
