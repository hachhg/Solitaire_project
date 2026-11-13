# CS449 Sprint 3

Python peg solitaire with manual and automated modes, randomization, recording
and replay. This folder is independent of the retained Sprint 2 code.
Only Python and Tkinter are needed; there are no pip dependencies.

## Open the game

In VS Code, choose **Terminal > New Terminal** and run:

```powershell
cd "C:\Users\hac23\CS449Sprint2"
py -m sprint3.solitaire_gui
```

On other computers, open a terminal in the repository root and use
`python -m sprint3.solitaire_gui`.

## Controls

1. Choose a board type, an odd size of at least 5, and Manual or Automated mode.
2. Click **New Game** to apply the settings. Changing a control by itself does
   not change the current game.
3. In Manual mode, click a peg and then an empty hole two cells away. Horizontal,
   vertical and diagonal jumps are allowed. **Hint** names one legal move.
4. In Automated mode, click **Autoplay**. **Pause** stops the timer; Autoplay
   resumes it. The computer chooses legal jumps, without promising a win.
5. **Randomize** rearranges the remaining pegs during an ongoing manual game.
   It preserves the board, peg count and move count. It may produce a position
   with no legal moves, which ends the game immediately.
6. **Record game** asks where to save a readable JSON text file. The initial
   position and every successful move or randomization are saved automatically.
   Recording can also begin partway through a game. Uncheck it to stop.
7. **Replay** opens a recording and shows its exact saved events. A replay
   uses the saved moves and randomized positions rather than generating new
   random choices. Autoplay/Pause also controls replay playback.

When recording is enabled, New Game asks for a file for the new recording.
Choose a different filename to retain earlier games. Cancel leaves the current
game intact. Invalid recording files do not replace the current game.

The result appears when one peg remains or no legal jumps remain. Ratings are
Outstanding for 1 peg, Very Good for 2, Good for 3, and Average for 4 or more.
The GUI labels start at 1. Code and recording coordinates start at 0.

## Tests

Run the 43 Sprint 3 tests:

```text
py -m unittest discover -s sprint3/tests -t . -v
```

Show the manual and automated game tests in the demonstration:

```text
py -m unittest sprint3.tests.test_game.ManualGameTests sprint3.tests.test_game.AutomatedGameTests -v
```

This command runs 13 tests: 9 manual tests and 4 automated tests.
Run all 78 project tests with `py -m unittest discover -v`.
For the 27 Sprint 3 tests that do not need a graphical desktop:

```text
py -m unittest sprint3.tests.test_game sprint3.tests.test_recording -v
```

## Classes

| File | Purpose |
| --- | --- |
| `board.py` | `Board` validates size/type and builds the three board shapes. |
| `game.py` | `PegSolitaireGame` owns shared rules and state. `ManualGame` adds randomization; `AutomatedGame` adds automatic move selection. `create_game` selects the class. |
| `recording.py` | `GameRecording` writes JSON text; `GameReplay` validates and applies saved events. |
| `solitaire_gui.py` | `SolitaireApp` displays controls and uses Tkinter timers. |
| `tests/` | Board, game, recording and GUI tests. |
| `__init__.py` and `tests/__init__.py` | Package setup, with no game rules. |

The English board uses the same plus shape as Sprint 2. The Hexagon and Diamond
use the same documented formulas. Pegs and counters are changed through game
methods; the public `pegs` property returns an immutable collection.

The mode is selected when New Game creates a model. The program replaces the
model when a new mode is chosen; it does not change an object's Python class.

## Reading the code

Start with `board.py`, then read `game.py`, `recording.py` and `solitaire_gui.py`.
The code uses named variables, ordinary loops and explicit conditions so each
step can be followed in order. GUI button availability is handled separately
by `_update_buttons`.

A few Python features used here:

- `@property` provides a getter, such as reading `game.peg_count`.
- `frozenset` is a set that callers cannot change.
- A leading underscore marks an internal field or helper by Python convention.
- `@classmethod` lets `GameReplay.load` return a new replay object from a file.
- Tkinter's `after` schedules one step, keeping the interface responsive.

## Assignment progress

The six required demonstration items are listed in [DEMO_GUIDE.md](DEMO_GUIDE.md).
Record a narrated video of at most five minutes and add its accessible link
to the report. The report's Part 2 design review and interaction screenshots
are deferred at the student's request.

OpenAI Codex assisted with the implementation, tests and report preparation.
