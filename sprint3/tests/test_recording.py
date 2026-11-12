"""Check file round trips, randomization replay and invalid recordings."""

import json
import tempfile
import unittest
from pathlib import Path

from sprint3.game import AutomatedGame, ManualGame
from sprint3.recording import GameRecording, GameReplay


class RecordingTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "game.json"

    def test_manual_moves_replay_every_position(self):
        game = ManualGame()
        recording = GameRecording(game)
        expected = [(game.pegs, game.move_count)]
        for _ in range(3):
            start, end = game.legal_moves()[0]
            game.move(start, end)
            recording.record_move(start, end)
            expected.append((game.pegs, game.move_count))
        recording.save(self.path)
        replay = GameReplay.load(self.path)
        self.assertEqual((replay.game.pegs, replay.game.move_count), expected[0])
        for state in expected[1:]:
            self.assertEqual(replay.step(), "move")
            self.assertEqual((replay.game.pegs, replay.game.move_count), state)
        self.assertTrue(replay.finished)
        self.assertIsNone(replay.step())

    def test_randomized_position_is_replayed_exactly(self):
        game = ManualGame(seed=1)
        game.move((1, 3), (3, 3))
        recording = GameRecording(game)
        initial = game.pegs
        game.randomize()
        recording.record_randomization(game)
        expected = game.pegs
        recording.save(self.path)
        replay = GameReplay.load(self.path)
        self.assertEqual(replay.game.pegs, initial)
        self.assertEqual(replay.step(), "randomize")
        self.assertEqual(replay.game.pegs, expected)
        self.assertEqual(replay.game.move_count, 1)

    def test_complete_automated_game_replays_same_result(self):
        game = AutomatedGame(5, "Hexagon", seed=4)
        recording = GameRecording(game)
        while True:
            move = game.auto_move()
            if move is None:
                break
            recording.record_move(*move)
        recording.save(self.path)
        replay = GameReplay.load(self.path)
        while replay.step():
            pass
        self.assertEqual(replay.game.MODE, "Automated")
        self.assertEqual(replay.game.pegs, game.pegs)
        self.assertEqual(replay.game.move_count, game.move_count)
        self.assertEqual(replay.game.rating(), game.rating())

    def test_recording_can_start_in_the_middle_of_a_game(self):
        game = ManualGame()
        game.move((1, 3), (3, 3))
        GameRecording(game).save(self.path)
        replay = GameReplay.load(self.path)
        self.assertTrue(replay.finished)
        self.assertEqual(replay.game.pegs, game.pegs)
        self.assertEqual(replay.game.move_count, 1)

    def test_truncated_file_is_rejected(self):
        self.path.write_text('{"version":', encoding="utf-8")
        with self.assertRaises(ValueError):
            GameReplay.load(self.path)

    def test_invalid_move_in_recording_is_rejected(self):
        recording = GameRecording(ManualGame())
        recording.record_move((0, 2), (3, 3))
        recording.save(self.path)
        with self.assertRaises(ValueError):
            GameReplay.load(self.path)

    def test_randomization_cannot_change_peg_count(self):
        GameRecording(ManualGame()).save(self.path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        data["events"] = [{"action": "randomize", "pegs": [[3, 3]]}]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            GameReplay.load(self.path)

    def test_file_errors_are_reported_to_caller(self):
        with self.assertRaises(OSError):
            GameRecording(ManualGame()).save(Path(self.folder.name) / "missing" / "game.json")
        with self.assertRaises(OSError):
            GameReplay.load(Path(self.folder.name) / "missing.json")


if __name__ == "__main__":
    unittest.main()
