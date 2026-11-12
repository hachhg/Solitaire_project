# Sprint 3 demonstration guide

Keep the narrated video under **five minutes**. Show all six items from the
assignment. Also include recording and replay, which are required in its
introduction. Practice once before recording.

## Open the game

In VS Code, open Terminal > New Terminal:

```powershell
cd "C:\Users\hac23\CS449Sprint2"
py -m sprint3.solitaire_gui
```

Use size 5 to keep the manual games short. A move is two clicks: source peg,
then empty destination. Coordinates below use GUI labels starting at **1**.
Read each pair as **row, column**. Rows go down; columns go across.

## Suggested recording order

1. **0:00 to 0:55 — English manual game.** Choose English, size 5, Manual, then
   New Game. Check Pegs 20 and Moves 0. Play the English moves below until the
   game-over message appears.

   Say: "This is my Sprint 3 Peg Solitaire game. I can choose the board size,
   type and game mode. First, I am playing a manual English game. I click a
   peg and then an empty hole two spaces away. The jumped peg is removed.
   The program checks for game over after each move."

2. **0:55 to 1:45 — Hexagon manual game.** Choose Hexagon, size 5, Manual, then
   New Game. Check Pegs 18 and Moves 0. Play the Hexagon moves below to the end.

   Say: "Next is a manual Hexagon game. The board shape changes, but it uses
   the same move rules. Horizontal, vertical and diagonal jumps are allowed.
   The final message shows the remaining pegs and rating."

3. **1:45 to 2:20 — Automated game and recording.** Choose English, size 5,
   Automated, then New Game. Check Record game and save as `sprint3_demo.json`.
   Click Autoplay and let the game end. Then uncheck Record game.

   Say: "In Automated mode, the computer chooses legal moves until the game
   ends. Autoplay can be paused and resumed. Recording saves the starting
   board and each successful action to a readable text file."

4. **2:20 to 3:40 — Manual game with randomization.** Choose English, size 5,
   Manual, then New Game. Use Hint to find a move, then click its two holes.
   Randomize after the second move and after the fourth move if the game is
   still ongoing. Continue using Hint and making moves until Game over.
   Do not use either fixed move list after randomization.

   Say: "This is manual play with periodic randomization. Randomize rearranges
   the remaining pegs while keeping the peg and move counts unchanged. I then
   continue choosing moves until no legal move remains. Hint suggests a move
   without performing it."

5. **3:40 to 4:05 — Replay.** Click Replay, open `sprint3_demo.json` and let it
   finish. Check that its final pegs and moves match the recorded game.

   Say: "Replay reads the saved file and repeats the exact recorded actions.
   It reaches the same final board instead of making new random choices."

6. **4:05 to 4:45 — Tests for both modes.** Switch to VS Code and run:

   ```text
   py -m unittest sprint3.tests.test_game.ManualGameTests sprint3.tests.test_game.AutomatedGameTests -v
   ```

   Show the named manual and automated tests, `Ran 13 tests` and `OK`.

   Say: "These automated unit tests check both game modes. The manual tests
   check valid and invalid jumps and game-over detection. The automated tests
   check legal move selection and automatic stopping. All thirteen tests pass."

## English size 5 manual moves

| Move | Source | Destination |
| --- | --- | --- |
| 1 | (1, 3) | (3, 3) |
| 2 | (2, 1) | (2, 3) |
| 3 | (2, 4) | (2, 2) |
| 4 | (3, 1) | (1, 3) |
| 5 | (3, 3) | (3, 1) |
| 6 | (3, 5) | (3, 3) |
| 7 | (4, 1) | (2, 1) |
| 8 | (4, 2) | (2, 4) |
| 9 | (1, 3) | (3, 5) |
| 10 | (4, 4) | (4, 2) |
| 11 | (5, 2) | (3, 2) |
| 12 | (2, 1) | (4, 3) |
| 13 | (5, 3) | (3, 3) |

Expected end: **7 pegs, 13 moves, Average**.

## Hexagon size 5 manual moves

| Move | Source | Destination |
| --- | --- | --- |
| 1 | (1, 1) | (3, 3) |
| 2 | (1, 3) | (1, 1) |
| 3 | (2, 4) | (2, 2) |
| 4 | (2, 1) | (2, 3) |
| 5 | (3, 3) | (1, 3) |
| 6 | (3, 1) | (3, 3) |
| 7 | (3, 4) | (3, 2) |
| 8 | (4, 2) | (2, 2) |
| 9 | (1, 1) | (3, 3) |
| 10 | (4, 3) | (2, 3) |
| 11 | (1, 3) | (3, 3) |
| 12 | (4, 4) | (2, 2) |

Expected end: **6 pegs, 12 moves, Average**.

Upload your finished narrated video to YouTube or Panopto. Check that your
instructor can open it, then paste its link into the report. Part 2 will be
completed separately, as requested.
