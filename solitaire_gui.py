"""Display a Solitaire settings demonstration."""

import tkinter as tk

class SolitaireSettings:
    """Display controls for choosing Solitaire settings."""

    def __init__(self, root):
        """Build the settings window."""
        self.root = root
        self.root.title("Solitaire Settings")

        #Store the checkbox and radio button selections.
        self.show_hints = tk.BooleanVar(value=True)
        self.draw_mode = tk.StringVar(value="Draw one")

        #Add the title at the top of the window.
        tk.Label(
            root,
            text="Solitaire Settings",
            font=("Arial", 20, "bold"),
        ).pack(pady=15)

        # Draw two horizontal lines below the title.
        canvas = tk.Canvas(root, width=360, height=20)
        canvas.pack()
        canvas.create_line(10, 5, 350, 5, width=2)
        canvas.create_line(10, 15, 350, 15, width=2)

        #The checkbox controls whether hints are enabled.
        tk.Checkbutton(
            root,
            text="Show hints",
            variable=self.show_hints,
        ).pack(pady=10)

        tk.Label(root, text="Choose a draw mode:").pack()

        #Sharing one variable makes the radio buttons exclusive.
        tk.Radiobutton(
            root,
            text="Draw one card",
            variable=self.draw_mode,
            value="Draw one",
        ).pack(pady=5)

        tk.Radiobutton(
            root,
            text="Draw three cards",
            variable=self.draw_mode,
            value="Draw three",
        ).pack(pady=5)

        # Clicking this button displays the selected settings.
        tk.Button(
            root,
            text="Apply Settings",
            command=self.apply_settings,
        ).pack(pady=15)

        self.status_label = tk.Label(
            root,
            text="Select your settings above.",
        )
        self.status_label.pack(padx=20, pady=15)

    def apply_settings(self):
        """Display the currently selected settings."""
        #Convert the checkbox value into readable text.
        hints = "On" if self.show_hints.get() else "Off"

        #Update the message at the bottom of the window.
        self.status_label.config(
            text=f"{self.draw_mode.get()} | Hints: {hints}"
        )


def main():
    """Run the GUI demonstration."""
    root = tk.Tk()
    SolitaireSettings(root)

    #Keep the window open and respond to user actions.
    root.mainloop()

if __name__ == "__main__":
    main()