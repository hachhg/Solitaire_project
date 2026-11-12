# Sprint 3 acceptance criteria

These criteria refine the eight user stories listed in the Sprint 3 assignment.
They are project criteria, not verbatim criteria supplied by the instructor.

| Story | Feature | Criteria |
| --- | --- | --- |
| 1 | Choose a board size and type | 1.1 Accept English, Hexagon and Diamond boards with odd sizes at least 5. 1.2 Reject invalid settings and preserve the current game. |
| 2 | Choose Manual or Automated mode | 2.1 Offer both modes. 2.2 Apply the selected mode on New Game. |
| 3 | Start a new game | 3.1 Use the selected size, shape and mode. 3.2 Fill all valid holes except the center, clear selection and reset moves to zero. |
| 4 | Make a manual move | 4.1 A legal jump removes the source and jumped peg, fills the destination and adds one move. 4.2 Reject illegal jumps without changing the pegs or move count. |
| 5 | End a manual game | 5.1 End when one peg remains or there are no legal moves. 5.2 Display the result, remaining pegs and rating. |
| 6 | Make an automated move | 6.1 Select and perform only a legal move using the shared rules. 6.2 Permit pause/resume and prevent manual board moves in automated mode. |
| 7 | End an automated game | 7.1 Stop automatically when no legal move remains or one peg remains. 7.2 Show the result and schedule no further moves. |
| 8 | Randomize during manual play | 8.1 Rearrange pegs inside the chosen shape while preserving peg count and move count. 8.2 Clear selection and check the result; disable randomization during automated play, replay and after game over. |

Additional recording requirements from the assignment introduction:

- R1 Save the starting board, mode, counters and successful moves/randomizations
  to a text file. Do not record rejected moves.
- R2 Load and validate a recording, then replay the exact events and final state.
  Invalid files leave the current game intact.
