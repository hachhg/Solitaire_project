# CS449 Peg Solitaire

Sprint 2 implements the manual Peg Solitaire BrainVita game in Python using
Tkinter and the xUnit-style `unittest` framework. No pip packages are needed.

## Run

Use Python 3.10 or newer with Tkinter installed. From the repository root, run:

```text
python -m sprint2.solitaire_gui
```

On Windows, `py -m sprint2.solitaire_gui` also works if the Python launcher is installed.
On Ubuntu/Debian, install the distribution's `python3-tk` package if necessary.

1. Choose an odd board size of at least 5 and a board type.
2. Click **New Game** to apply the selected settings.
3. Click a peg, then an empty hole exactly two positions away in a straight line.
4. Horizontal, vertical and diagonal jumps are allowed, as stated in the homework
   overview. Each jump removes the peg between the start and destination.
5. The game automatically ends when one peg remains or no jump is available.

The result shows the remaining peg count and rating: Outstanding for one peg,
Very Good for two, Good for three, and Average for four or more.

## Test

```text
python -m unittest discover -v
```

Run the test command from the repository root. It runs 35 tests, including
33 Sprint 2 tests and 2 retained Sprint 0 tests. A graphical
desktop is needed for `test_gui.py`; its windows remain hidden.

To run only the 27 tests that do not need a graphical desktop:

```text
python -m unittest sprint2.test_game test_deck -v
```

## Structure

| File | Responsibility |
| --- | --- |
| `board.py` | `Board` validates settings and builds each shape's valid holes. |
| `game.py` | `PegSolitaireGame` handles initialization, jumps, results and ratings. |
| `solitaire_gui.py` | `SolitaireApp` displays controls, draws holes and handles clicks. |
| `test_game.py` | Board and game-rule unit tests, including the two identified AI-generated tests. |
| `test_gui.py` | Tests settings controls, click handlers and result messages. |
| `../deck.py`, `../test_deck.py`, `../solitaire_gui.py` | Retained Sprint 0 card-deck exercise and settings demonstration at the repository root; unused by the peg-solitaire game. |

The game model imports no GUI library, so its rules can be tested independently
and another interface can use the same model.

## Board definitions

Size is the width and height of the enclosing square grid. The center starts
empty and every other valid hole contains a peg. Coordinates in the code are
zero-based `(row, column)`; the GUI's edge labels start at 1.

- **English:** a cross with a central horizontal and vertical band three holes
  wide. Size 7 has 33 holes and starts with 32 pegs.
- **Hexagon:** the enclosing square with two opposite corners removed; the
  condition is `abs(row - column) <= size // 2`. Size 7 has row lengths
  4, 5, 6, 7, 6, 5, 4, giving 37 holes and 36 starting pegs.
- **Diamond:** Manhattan distance from the center is at most `size // 2`.
  Size 7 has 25 holes and starts with 24 pegs.

These size and shape definitions make the board choices precise; the overview
does not specify a formula for every board size.

## Requirements update from Sprint 1

Sprint 2 combines choosing size and type into User Story 1 to match the new
report tables. New game, movement and game-over stories become 2, 3 and 4.
The move criteria now include diagonal jumps because the homework overview
explicitly permits them. The report records the full updated criteria.

Autoplay, randomization and recording/replay belong to later sprints.

## AI assistance

OpenAI Codex assisted with this Sprint 2 implementation, tests and report.
`GameTests.test_valid_jump_updates_all_three_holes` and
`GameTests.test_invalid_jump_leaves_board_unchanged` are the two tests identified
for the assignment's LLM evidence. The tests were run and their expected states
checked against the project rules; the report explains the validation.
