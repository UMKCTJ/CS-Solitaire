import tkinter as tk

CELL = 40          
BOARD_SIZE = 7

class SolitaireGUI:
    def __init__(self, root):
        self.root = root
        root.title("Peg Solitaire")

        # Text (Title & Board Size)
        tk.Label(root, text="Solitaire", font=("Helvetica", 16, "bold")
                 ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        tk.Label(root, text=f"Board size: {BOARD_SIZE}", font=("Helvetica", 11)
                 ).grid(row=0, column=2, sticky="e", padx=10)

        # Radio Buttons (Borad Type)
        left = tk.Frame(root)
        left.grid(row=1, column=0, sticky="n", padx=10)
        tk.Label(left, text="Board Type", font=("Helvetica", 11)).pack(anchor="w")
        self.board_type = tk.StringVar(value="English")
        for name in ("English", "Hexagon", "Diamond"):
            tk.Radiobutton(left, text=name, variable=self.board_type,
                           value=name).pack(anchor="w", padx=10)

        # Lines (the actual board itself. Size may vary.)
        size = CELL * BOARD_SIZE
        self.canvas = tk.Canvas(root, width=size + 2, height=size + 2,
                                bg="white", highlightthickness=0)
        self.canvas.grid(row=1, column=1, padx=20)
        self.draw_english_board()

        # Check Box (Record game)
        self.record = tk.BooleanVar(value=False)
        tk.Checkbutton(root, text="Record game", variable=self.record
                       ).grid(row=2, column=0, sticky="w", padx=10, pady=10)

    @staticmethod
    def is_on_board(row, col):
        """English board: a plus shape (middle 3 rows or middle 3 columns)."""
        return 2 <= row <= 4 or 2 <= col <= 4

    def draw_english_board(self):
        c = self.canvas
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if not self.is_on_board(row, col):
                    continue
                x1, y1 = col * CELL + 1, row * CELL + 1
                x2, y2 = x1 + CELL, y1 + CELL
                # Square drawn with four lines
                c.create_line(x1, y1, x2, y1) # top
                c.create_line(x1, y2, x2, y2) # bottom
                c.create_line(x1, y1, x1, y2) # left
                c.create_line(x2, y1, x2, y2) # right
                # Peg in every hole except center
                if (row, col) != (3, 3):
                    cx, cy, r = (x1 + x2) / 2, (y1 + y2) / 2, 6
                    c.create_oval(cx - r, cy - r, cx + r, cy + r, fill="black")


if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireGUI(root)
    root.mainloop()