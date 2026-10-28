# Sprint 2 narrated demo guide

Aim for about 2 minutes 30 seconds. Record the running app and then the test
results. Use your own voice and explain what you are showing. Upload the finished
video to YouTube or Panopto and confirm the instructor can open its link.

## 0:00 to 0:25 - Explain the program

"This is my CS449 Sprint 2 peg-solitaire game. It uses Python and Tkinter.
Board creates the board shape, PegSolitaireGame handles the rules, and
SolitaireApp handles the display. The interface and game logic are separate."

Show English size 7. It has a plus-shaped board, 32 pegs, and an empty center.

## 0:25 to 0:50 - Settings and a new game

"I can choose English, Hexagon, or Diamond and an odd board size from 5.
Changing a setting leaves the current game alone until I click New Game."

Select Hexagon, click New Game, and show its shape. Then select Diamond,
set size to 5, and click New Game. The Diamond board starts with 12 pegs.

## 0:50 to 1:40 - Moves and automatic game over

"A move jumps over one peg into an empty cell two positions away. The middle
peg is removed. Horizontal, vertical and diagonal jumps are allowed."

The edge numbers are **row, column**, starting at 1. On a fresh Diamond size 5,
click each source cell and then its destination, in this order:

| Move | Source row, column | Destination row, column |
| --- | --- | --- |
| 1 | 1, 3 | 3, 3 |
| 2 | 3, 1 | 1, 3 |
| 3 | 3, 3 | 3, 1 |
| 4 | 3, 5 | 3, 3 |
| 5 | 1, 3 | 3, 5 |
| 6 | 4, 2 | 2, 4 |
| 7 | 3, 5 | 1, 3 |
| 8 | 4, 4 | 4, 2 |

After move 1, you can demonstrate an invalid attempt by selecting the peg at
(1, 3), which is now empty: the app asks you to choose a peg first. To show an
invalid jump instead, choose (3, 1), click occupied (3, 2), then click (1, 3)
to complete the valid move 2 with the original selection.

After move 8, the result is **4 pegs, 8 moves, Game over, Average**.

"The program detects that there are no legal moves and shows the remaining
pegs and rating. A single peg would be a win with an Outstanding rating."

## 1:40 to 2:15 - Automated tests

Run:

```text
python -m unittest discover -v
```

"These are 35 passing automated tests using unittest. They check board shapes,
settings, legal jumps in all eight directions, rejected moves, game-over cases,
and the GUI event handlers. The two tests marked AI-generated check a valid
jump's full state change and an invalid jump leaving the board unchanged."

Make sure the video visibly includes **Ran 35 tests** and **OK**.

## 2:15 to 2:30 - Show the code and repository

Show board.py, game.py and solitaire_gui.py briefly, then the public GitHub link
in the report. Explain that the test files are in the same repository.

## Before submitting

Add the video URL and screenshots of the AI prompts and responses to the report.
Screenshots must come from the actual conversation; a pasted transcript alone
does not replace the assignment's screenshot requirement. Confirm both links
work without your own signed-in account, then upload the DOCX to Canvas.
