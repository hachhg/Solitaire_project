"""Tkinter interface for the CS449 Sprint 2 peg-solitaire game."""

import tkinter as tk
from tkinter import ttk

from .board import Board
from .game import PegSolitaireGame


class SolitaireApp:
    """Display settings and translate clicks into requests to the game model."""

    def __init__(self, root):
        self.root = root
        root.title("CS449 Peg Solitaire - Sprint 2")
        root.geometry("900x650")
        root.minsize(800, 580)
        root.configure(bg="white")
        self.game = PegSolitaireGame()
        self.selected = None
        self.size_var = tk.StringVar(value="7")
        self.type_var = tk.StringVar(value="English")
        self.status_var = tk.StringVar()
        self.summary_var = tk.StringVar()
        self.centers = {}
        self.cell_half_size = 20

        self._build_controls()
        self.refresh("Choose a peg, then click an empty hole two positions away.")

    def _build_controls(self):
        """Build the controls; all move rules stay inside PegSolitaireGame."""
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TLabel", background="white", font=("Arial", 11))
        style.configure("TFrame", background="white")
        style.configure("TRadiobutton", background="white", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 12), padding=(10, 6))

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        # Title and board size at the top of the window.
        header = ttk.Frame(frame)
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(
            header, text="Peg Solitaire", font=("Arial", 17),
        ).pack(side="left")
        self.size_input = ttk.Spinbox(
            header, from_=5, to=99, increment=2, width=5,
            textvariable=self.size_var,
        )
        self.size_input.pack(side="right")
        ttk.Label(header, text="Board size").pack(side="right", padx=(0, 10))

        # Board types on the left, board in the center, New Game on the right.
        body = ttk.Frame(frame)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        choices = ttk.Frame(body, padding=(0, 18, 12, 0))
        choices.grid(row=0, column=0, sticky="nw")
        ttk.Label(choices, text="Board Type", font=("Arial", 12)).pack(anchor="w")
        for name in Board.TYPES:
            ttk.Radiobutton(
                choices, text=name, value=name, variable=self.type_var,
            ).pack(anchor="w", padx=(14, 0), pady=2)

        self.canvas = tk.Canvas(body, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", self.draw_board)

        actions = ttk.Frame(body, padding=(14, 64, 0, 0))
        actions.grid(row=0, column=2, sticky="ne")
        self.new_game_button = ttk.Button(
            actions, text="New Game", command=self.start_new_game,
        )
        self.new_game_button.pack()

        # Counts, feedback and instructions below the board.
        ttk.Label(
            frame, textvariable=self.summary_var, font=("Arial", 11, "bold"),
        ).pack(anchor="w", pady=(12, 7))
        self.status_label = ttk.Label(
            frame, textvariable=self.status_var, wraplength=830,
        )
        self.status_label.pack(anchor="w")
        ttk.Label(
            frame,
            text=("Jump horizontally, vertically or diagonally. "
                  "Click a peg, then an empty cell."),
            font=("Arial", 10),
        ).pack(anchor="w", pady=(7, 0))

    def start_new_game(self):
        """Validate settings and reset the board, or preserve the existing game."""
        try:
            size = int(self.size_var.get().strip())
            self.game.new_game(size, self.type_var.get())
        except ValueError as error:
            self.size_var.set(str(self.game.board.size))
            self.status_var.set(f"Invalid settings: {error}")
            return False

        self.selected = None
        self.refresh("New game started. Select a peg and its destination.")
        return True

    def on_canvas_click(self, event):
        """Convert a click inside a displayed hole into its board coordinate."""
        for position, (x, y) in self.centers.items():
            inside_x = abs(event.x - x) <= self.cell_half_size
            inside_y = abs(event.y - y) <= self.cell_half_size
            if inside_x and inside_y:
                self.select_hole(position)
                return

        self.status_var.set("Click a peg or an empty hole inside the board.")

    def select_hole(self, position):
        """Select a peg or ask the model to move the selected peg."""
        if self.game.is_game_over():
            self.refresh()
            return

        if position not in self.game.holes:
            self.status_var.set("Invalid move: that position is outside the board.")
            return

        if self.selected is None:
            if position in self.game.pegs:
                self.selected = position
                self.refresh("Peg selected. Click an empty hole two positions away.")
            else:
                self.status_var.set("Choose a peg first, then its empty destination.")
            return

        if position == self.selected:
            self.selected = None
            self.refresh("Selection cleared. Choose another peg.")
            return

        if self.game.move(self.selected, position):
            self.selected = None
            self.refresh("Valid jump. Choose your next peg.")
        else:
            self.refresh(
                "Invalid move. Jump exactly two positions over one peg "
                "into an empty hole."
            )

    def refresh(self, message=None):
        """Refresh the counts and show the result as soon as the game ends."""
        board = self.game.board
        self.summary_var.set(
            f"{board.board_type} {board.size} x {board.size}"
            f"   |   Pegs: {self.game.peg_count}"
            f"   |   Moves: {self.game.move_count}"
        )
        if self.game.is_game_over():
            if self.game.is_won():
                result = "You won!"
            else:
                result = "Game over - no legal moves."
            self.status_var.set(
                f"{result} {self.game.peg_count} peg(s) left. "
                f"Rating: {self.game.rating()}. "
                "Click New Game to play again."
            )
        elif message:
            self.status_var.set(message)
        self.draw_board()

    def draw_board(self, event=None):
        """Draw a grid of square holes with small pegs, like the course sample."""
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 100)
        height = max(self.canvas.winfo_height(), 100)
        size = self.game.board.size
        cell_size = min((width - 70) / size, (height - 70) / size)
        self.cell_half_size = cell_size / 2
        first_x = (width - (size - 1) * cell_size) / 2
        first_y = (height - (size - 1) * cell_size) / 2
        self.centers = {}

        for row, column in sorted(self.game.holes):
            x = first_x + column * cell_size
            y = first_y + row * cell_size
            self.centers[(row, column)] = (x, y)

            color = "#fff0b3" if (row, column) == self.selected else "white"
            half = self.cell_half_size
            self.canvas.create_rectangle(
                x - half, y - half, x + half, y + half,
                fill=color, outline="#333333", width=1.5,
            )
            if (row, column) in self.game.pegs:
                peg_radius = max(2, cell_size * 0.145)
                self.canvas.create_oval(
                    x - peg_radius, y - peg_radius,
                    x + peg_radius, y + peg_radius,
                    fill="#222222", outline="#222222",
                )

        # Hide coordinate labels when the cells are too small to read them.
        if cell_size >= 28:
            for index in range(size):
                self.canvas.create_text(
                    first_x + index * cell_size, first_y - cell_size * 0.8,
                    text=str(index + 1), fill="#777777", font=("Arial", 8),
                )
                self.canvas.create_text(
                    first_x - cell_size * 0.8, first_y + index * cell_size,
                    text=str(index + 1), fill="#777777", font=("Arial", 8),
                )


def main():
    """Launch the manual peg-solitaire game."""
    root = tk.Tk()
    SolitaireApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
