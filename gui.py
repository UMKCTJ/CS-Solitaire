import tkinter as tk
from tkinter import messagebox

from logic import (BOARD_TYPES, DEFAULT_SIZE, DEFAULT_TYPE, EMPTY,
                    MAX_SIZE, MIN_SIZE, PEG, SolitaireGame)
BOARD_PIXELS = 360

class SolitaireGUI:
    def __init__(self, root):
        self.root = root
        root.title("Peg Solitaire")
        self.game = SolitaireGame(DEFAULT_TYPE, DEFAULT_SIZE)

        # Text & Board Size
        tk.Label(root, text="Peg Solitaire", font=("Helvetica", 16, "bold")
                 ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        size_frame = tk.Frame(root)
        size_frame.grid(row=0, column=2, sticky="e", padx=10)
        tk.Label(size_frame, text="Board size").pack(side="left")
        self.size_var = tk.StringVar(master=root, value=str(DEFAULT_SIZE))
        size_box = tk.Spinbox(size_frame, from_=MIN_SIZE, to=MAX_SIZE, increment=2,
                              width=4, textvariable=self.size_var,
                              command=self.on_size_change)
        size_box.pack(side="left", padx=5)
        size_box.bind("<Return>", lambda e: self.on_size_change())
        size_box.bind("<FocusOut>", lambda e: self.on_size_change())

        # Board Type
        left = tk.Frame(root)
        left.grid(row=1, column=0, sticky="n", padx=10)
        tk.Label(left, text="Board Type").pack(anchor="w")
        self.type_var = tk.StringVar(master=root, value=DEFAULT_TYPE)
        for name in BOARD_TYPES:
            tk.Radiobutton(left, text=name, variable=self.type_var, value=name,
                           command=self.on_type_change).pack(anchor="w", padx=10)

        # The Board
        self.canvas = tk.Canvas(root, width=BOARD_PIXELS + 2, height=BOARD_PIXELS + 2,
                                bg="white", highlightthickness=0)
        self.canvas.grid(row=1, column=1, padx=20)
        self.canvas.bind("<Button-1>", self.on_click)

        # New Game
        tk.Button(root, text="New Game", width=10, command=self.on_new_game
                  ).grid(row=1, column=2, sticky="n", padx=10, pady=40)

        # Record & Status
        self.record_var = tk.BooleanVar(master=root, value=False)
        tk.Checkbutton(root, text="Record game", variable=self.record_var
                       ).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.status = tk.Label(root, text="", font=("Helvetica", 11),
                               wraplength=420, justify="left")
        self.status.grid(row=2, column=1, columnspan=2, sticky="w", pady=10)

        self.refresh()

    # Confirm
    def confirm_abandon(self):
        if not self.game.is_in_progress():
            return True
        return messagebox.askyesno(
            "Abandon game?", "The current game will be abandoned. Continue?")

    def on_size_change(self):
        if self.size_var.get() == str(self.game.size):
            return
        if not self.confirm_abandon():
            self.size_var.set(str(self.game.size))
            return
        if not self.game.set_size(self.size_var.get()):
            # Revert to last valid size
            self.size_var.set(str(self.game.size))   
        self.refresh()

    def on_type_change(self):
        if self.type_var.get() == self.game.board_type:
            return
        if not self.confirm_abandon():
            self.type_var.set(self.game.board_type)
            return
        self.game.set_board_type(self.type_var.get())
        self.refresh()

    def on_new_game(self):
        self.game.new_game()
        self.refresh()

    def on_click(self, event):
        cell = self.cell_px()
        self.game.click(event.y // cell, event.x // cell)
        self.refresh()

    # Draw / Update Board
    def cell_px(self):
        return BOARD_PIXELS // self.game.board.size

    def refresh(self):
        self.draw_board()
        self.status.config(text=self.game.message)

    def draw_board(self):
        c = self.canvas
        c.delete("all")
        board = self.game.board
        cell = self.cell_px()
        r_peg = cell // 4
        targets = self.game.get_highlighted_destinations()
        for row in range(board.size):
            for col in range(board.size):
                state = board.get_cell(row, col)
                if state not in (PEG, EMPTY):
                    continue
                x1, y1 = col * cell + 1, row * cell + 1
                x2, y2 = x1 + cell, y1 + cell
                # Square drawn with four lines
                c.create_line(x1, y1, x2, y1)
                c.create_line(x1, y2, x2, y2)
                c.create_line(x1, y1, x1, y2)
                c.create_line(x2, y1, x2, y2)
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                box = (cx - r_peg, cy - r_peg, cx + r_peg, cy + r_peg)
                if state == PEG:
                    color = "red" if self.game.selected == (row, col) else "black"
                    c.create_oval(*box, fill=color)
                elif (row, col) in targets:
                    c.create_oval(*box, fill="light green", outline="green")
                else:
                    c.create_oval(*box, outline="gray")