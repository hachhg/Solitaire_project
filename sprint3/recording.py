"""Save game events as readable JSON text and replay validated recordings."""

import json
from pathlib import Path

from .game import create_game


class GameRecording:
    """Store the starting position and each successful game action."""

    def __init__(self, game):
        self._data = {
            "version": 1,
            "size": game.board.size,
            "board_type": game.board.board_type,
            "mode": game.MODE,
            "initial_pegs": [list(position) for position in sorted(game.pegs)],
            "initial_moves": game.move_count,
            "events": [],
        }

    def record_move(self, start, end):
        self._data["events"].append({
            "action": "move", "start": list(start), "end": list(end),
        })

    def record_randomization(self, game):
        self._data["events"].append({
            "action": "randomize",
            "pegs": [list(position) for position in sorted(game.pegs)],
        })

    def save(self, path):
        """Write text that can be opened in an ordinary text editor."""
        Path(path).write_text(json.dumps(self._data, indent=2) + "\n", encoding="utf-8")


class GameReplay:
    """Read a recording and apply its events one at a time."""

    def __init__(self, data):
        self._data = data
        self.restart()

    @classmethod
    def load(cls, path):
        """Validate the entire file before it replaces a game in the GUI."""
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") != 1:
                raise ValueError("Unsupported recording format.")
            if not isinstance(data["events"], list):
                raise ValueError("The recording needs a list of events.")
            replay = cls(data)
            while replay.step():
                pass
            replay.restart()
            return replay
        except (KeyError, TypeError, ValueError, AttributeError) as error:
            raise ValueError("Invalid game recording: " + str(error)) from error

    @property
    def finished(self):
        return self._index == len(self._data["events"])

    def restart(self):
        self.game = create_game(
            self._data["size"], self._data["board_type"], self._data["mode"],
        )
        self.game.restore_position(self._data["initial_pegs"], self._data["initial_moves"])
        self._index = 0

    def step(self):
        """Apply the next event and return its action, or None at the end."""
        if self.finished:
            return None
        event = self._data["events"][self._index]
        if self.game.is_game_over():
            raise ValueError("An event occurs after the game ended.")
        action = event["action"]
        if action == "move":
            start = self._coordinate(event["start"])
            end = self._coordinate(event["end"])
            if not self.game.move(start, end):
                raise ValueError("The recording contains an illegal move.")
        elif action == "randomize" and self.game.MODE == "Manual":
            count = self.game.peg_count
            self.game.restore_position(event["pegs"], self.game.move_count)
            if self.game.peg_count != count:
                raise ValueError("Randomization changed the number of pegs.")
        else:
            raise ValueError("Unknown action or randomization in automated mode.")
        self._index += 1
        return action

    @staticmethod
    def _coordinate(value):
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("A move needs a row and column.")
        if any(type(number) is not int for number in value):
            raise ValueError("Move coordinates must be whole numbers.")
        return tuple(value)
