"""Tkinter controls for manual play, automated play and recorded games."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from .board import Board
from .game import ManualGame, create_game
from .recording import GameRecording, GameReplay


class SolitaireApp:
    """Translate buttons and clicks into requests to the game classes."""

    DELAY_MS = 350

    def __init__(self, root):
        self.root = root
        root.title("CS449 Peg Solitaire - Sprint 3")
        root.geometry("1000x720")
        root.minsize(900, 650)
        root.configure(bg="white")
        self.game = ManualGame()
        self.selected = None
        self.replay = None
        self.recording = None
        self.recording_path = None
        self.running = False
        self._timer_id = None
        self.size_var = tk.StringVar(value="7")
        self.type_var = tk.StringVar(value="English")
        self.mode_var = tk.StringVar(value="Manual")
        self.record_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar()
        self.summary_var = tk.StringVar()
        self.file_var = tk.StringVar(value="Recording off")
        self.centers = {}
        self.cell_half_size = 20
        self._build_controls()
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh("Choose settings and click New Game. Use Hint if you need a move.")

    def _build_controls(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        for name in ("TFrame", "TLabel", "TRadiobutton", "TCheckbutton"):
            style.configure(name, background="white")
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TRadiobutton", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 12), padding=(10, 6))
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)
        header = ttk.Frame(frame)
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(header, text="Peg Solitaire", font=("Arial", 17)).pack(side="left")
        ttk.Spinbox(header, from_=5, to=99, increment=2, width=5,
                    textvariable=self.size_var).pack(side="right")
        ttk.Label(header, text="Board size").pack(side="right", padx=(0, 10))

        body = ttk.Frame(frame)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        choices = ttk.Frame(body, padding=(0, 18, 12, 0))
        choices.grid(row=0, column=0, sticky="nw")
        ttk.Label(choices, text="Board Type").pack(anchor="w")
        for name in Board.TYPES:
            ttk.Radiobutton(choices, text=name, value=name,
                            variable=self.type_var).pack(anchor="w", pady=3)
        ttk.Label(choices, text="Game Mode").pack(anchor="w", pady=(25, 3))
        for name in ("Manual", "Automated"):
            ttk.Radiobutton(choices, text=name, value=name,
                            variable=self.mode_var).pack(anchor="w", pady=3)

        self.canvas = tk.Canvas(body, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", self.draw_board)
        actions = ttk.Frame(body, padding=(14, 20, 0, 0))
        actions.grid(row=0, column=2, sticky="ne")
        self.replay_button = ttk.Button(actions, text="Replay", command=self.open_replay)
        self.replay_button.pack(fill="x", pady=4)
        self.new_game_button = ttk.Button(actions, text="New Game", command=self.start_new_game)
        self.new_game_button.pack(fill="x", pady=4)
        self.auto_button = ttk.Button(actions, text="Autoplay", command=self.toggle_autoplay)
        self.auto_button.pack(fill="x", pady=(35, 4))
        self.random_button = ttk.Button(actions, text="Randomize", command=self.randomize_board)
        self.random_button.pack(fill="x", pady=4)
        self.hint_button = ttk.Button(actions, text="Hint", command=self.show_hint)
        self.hint_button.pack(fill="x", pady=4)
        self.record_check = ttk.Checkbutton(
            frame, text="Record game", variable=self.record_var,
            command=self.change_recording,
        )
        self.record_check.pack(anchor="w", pady=(12, 3))
        ttk.Label(frame, textvariable=self.file_var, font=("Arial", 9)).pack(anchor="w")
        ttk.Label(frame, textvariable=self.summary_var,
                  font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 6))
        ttk.Label(frame, textvariable=self.status_var, wraplength=940).pack(anchor="w")
        ttk.Label(frame, text="Click a peg, then an empty hole two spaces away. "
                  "Horizontal, vertical and diagonal jumps are allowed.",
                  font=("Arial", 10)).pack(anchor="w", pady=(6, 0))

    def start_new_game(self):
        """Create a new model before replacing any existing game or timer."""
        try:
            size = int(self.size_var.get())
            board_type = self.type_var.get()
            mode = self.mode_var.get()
            game = create_game(size, board_type, mode)
        except ValueError as error:
            self.status_var.set(f"Invalid settings: {error}")
            return False
        recording = None
        path = None
        if self.record_var.get():
            path = self._choose_recording_path()
            if not path:
                return False
            recording = GameRecording(game)
            try:
                recording.save(path)
            except OSError as error:
                self.status_var.set(f"Could not save recording: {error}")
                return False
        self._cancel_timer()
        self.game = game
        self.selected = None
        self.replay = None
        self.recording = recording
        self.recording_path = path
        if path:
            self.file_var.set(f"Recording to {Path(path).name}")
        else:
            self.file_var.set("Recording off")
        self.refresh("New game started. Click Autoplay in automated mode, or choose a peg.")
        return True

    def on_canvas_click(self, event):
        for position, (x, y) in self.centers.items():
            inside_x = abs(event.x - x) <= self.cell_half_size
            inside_y = abs(event.y - y) <= self.cell_half_size
            if inside_x and inside_y:
                self.select_hole(position)
                return
        self.status_var.set("Click inside a hole on the board.")

    def select_hole(self, position):
        if self.replay is not None or self.game.MODE != "Manual":
            self.status_var.set("Board clicks are available in Manual mode. Click New Game to change modes.")
            return
        if self.game.is_game_over():
            self.refresh()
            return
        if position not in self.game.get_holes():
            self.status_var.set("That position is outside the board.")
        elif self.selected is None:
            if position in self.game.get_pegs():
                self.selected = position
                self.refresh("Peg selected. Click its empty destination.")
            else:
                self.status_var.set("Choose a peg first.")
        elif position == self.selected:
            self.selected = None
            self.refresh("Selection cleared.")
        elif self.game.move(self.selected, position):
            if self.recording is not None:
                self.recording.record_move(self.selected, position)
            self.selected = None
            error = self._save_recording()
            if error is not None:
                self.refresh(error)
            else:
                self.refresh("Valid jump. Choose your next peg, or click Hint.")
        else:
            self.refresh("Invalid move. Jump two spaces over one peg into an empty hole.")

    def show_hint(self):
        if self.replay is not None or self.game.MODE != "Manual":
            return
        moves = self.game.legal_moves()
        if moves:
            start, end = moves[0]
            self.selected = None
            self.refresh(f"Hint: click row {start[0] + 1}, column {start[1] + 1}, "
                         f"then row {end[0] + 1}, column {end[1] + 1}.")
        else:
            self.refresh()

    def randomize_board(self):
        if self.replay is not None or self.game.MODE != "Manual":
            return False
        if not self.game.randomize():
            self.refresh()
            return False
        self.selected = None
        if self.recording is not None:
            self.recording.record_randomization(self.game)
        error = self._save_recording()
        if error is not None:
            self.refresh(error)
        else:
            self.refresh("Board randomized. Peg and move counts are unchanged.")
        return True

    def toggle_autoplay(self):
        if self.replay is not None:
            if self.replay.is_finished():
                return
        elif self.game.MODE != "Automated" or self.game.is_game_over():
            return
        if self.running:
            self._cancel_timer()
            self.refresh("Paused. Click Autoplay to continue.")
        else:
            self.running = True
            if self.replay is not None:
                self.refresh("Replaying recording...")
            else:
                self.refresh("Automated game running...")
            self._timer_id = self.root.after(self.DELAY_MS, self.tick)

    def tick(self):
        """Run one replay event or automated move without blocking Tkinter."""
        self._timer_id = None
        if not self.running:
            return
        if self.replay is not None:
            action = self.replay.step()
            self.game = self.replay.game
            message = f"Replay: {action}."
            if self.replay.is_finished():
                self.running = False
                message = "Replay finished. Click Replay to open a recording again."
        else:
            move = self.game.auto_move()
            if move is not None and self.recording is not None:
                start, end = move
                self.recording.record_move(start, end)
            error = self._save_recording()
            if error is not None:
                message = error
            else:
                message = "Automated jump completed."
            if self.game.is_game_over():
                self.running = False
        self.refresh(message)
        if self.running:
            self._timer_id = self.root.after(self.DELAY_MS, self.tick)

    def _cancel_timer(self):
        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        self.running = False

    def _choose_recording_path(self):
        return filedialog.asksaveasfilename(
            parent=self.root, title="Save game recording", defaultextension=".json",
            filetypes=[("Game recordings", "*.json"), ("Text files", "*.txt")],
        )

    def change_recording(self):
        if not self.record_var.get():
            self.recording = None
            self.recording_path = None
            self.file_var.set("Recording off")
            return
        path = self._choose_recording_path()
        if not path:
            self.record_var.set(False)
            return
        self.recording = GameRecording(self.game)
        self.recording_path = path
        self._save_recording()

    def _save_recording(self):
        if self.recording is None:
            return None
        try:
            self.recording.save(self.recording_path)
            self.file_var.set(f"Recording to {Path(self.recording_path).name}")
        except OSError as error:
            message = f"Game updated, but recording could not be saved: {error}"
            self.recording = None
            self.recording_path = None
            self.record_var.set(False)
            self.file_var.set("Recording stopped because saving failed")
            self.status_var.set(message)
            return message
        return None

    def open_replay(self):
        path = filedialog.askopenfilename(
            parent=self.root, title="Open game recording",
            filetypes=[("Game recordings", "*.json *.txt"), ("All files", "*.*")],
        )
        if not path:
            return False
        try:
            replay = GameReplay.load(path)
        except (OSError, ValueError) as error:
            self.status_var.set(f"Could not open recording: {error}")
            return False
        self._cancel_timer()
        self.replay = replay
        self.game = replay.game
        self.selected = None
        self.recording = None
        self.recording_path = None
        self.record_var.set(False)
        self.size_var.set(str(self.game.get_board().get_size()))
        self.type_var.set(self.game.get_board().get_board_type())
        self.mode_var.set(self.game.MODE)
        self.file_var.set(f"Replaying {Path(path).name}")
        self.refresh("Recording loaded.")
        if not replay.is_finished():
            self.toggle_autoplay()
        else:
            self.refresh("Replay finished. This recording contains its starting position only.")
        return True

    def refresh(self, message=None):
        """Show the current counts, message, button states and board."""
        board = self.game.get_board()
        mode = self.game.MODE
        if self.replay is not None:
            mode = "Replay"
        self.summary_var.set(f"{board.get_board_type()} {board.get_size()} x {board.get_size()} | {mode}"
                             f" | Pegs: {self.game.get_peg_count()} | Moves: {self.game.get_move_count()}")
        game_over = self.game.is_game_over()
        if game_over:
            if self.game.is_won():
                result = "You won!"
            else:
                result = "Game over - no legal moves."
            text = f"{result} {self.game.get_peg_count()} peg(s) left. Rating: {self.game.rating()}."
            if self.replay is not None and self.replay.is_finished():
                text += " Replay finished."
            if message and "could not be saved" in message:
                text += " " + message
            self.status_var.set(text)
        elif message:
            self.status_var.set(message)
        self._update_buttons(game_over)
        self.draw_board()

    def _update_buttons(self, game_over):
        """Enable the controls that are available in the current game mode."""
        self.random_button.configure(state="disabled")
        self.hint_button.configure(state="disabled")
        self.auto_button.configure(state="disabled", text="Autoplay")
        self.record_check.configure(state="normal")

        if self.running:
            self.auto_button.configure(text="Pause")

        if self.replay is not None:
            self.record_check.configure(state="disabled")
            if not self.replay.is_finished():
                self.auto_button.configure(state="normal")
        elif not game_over:
            if self.game.MODE == "Manual":
                self.random_button.configure(state="normal")
                self.hint_button.configure(state="normal")
            else:
                self.auto_button.configure(state="normal")

    def close(self):
        self._cancel_timer()
        self.root.destroy()

    def draw_board(self, event=None):
        """Draw a grid of square holes with small pegs, like the course sample."""
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 100)
        height = max(self.canvas.winfo_height(), 100)
        size = self.game.get_board().get_size()
        cell_size = min((width - 70) / size, (height - 70) / size)
        self.cell_half_size = cell_size / 2
        first_x = (width - (size - 1) * cell_size) / 2
        first_y = (height - (size - 1) * cell_size) / 2
        self.centers = {}

        for row, column in sorted(self.game.get_holes()):
            x = first_x + column * cell_size
            y = first_y + row * cell_size
            self.centers[(row, column)] = (x, y)

            color = "white"
            if (row, column) == self.selected:
                color = "#fff0b3"
            half = self.cell_half_size
            self.canvas.create_rectangle(
                x - half, y - half, x + half, y + half,
                fill=color, outline="#333333", width=1.5,
            )
            if (row, column) in self.game.get_pegs():
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
    root = tk.Tk()
    SolitaireApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
