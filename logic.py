# Cell states
INVALID = -1
EMPTY = 0 
PEG = 1 

# Orthogonal and diagonal
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (-1, 1), (1, -1), (1, 1)]
MIN_SIZE = 5
MAX_SIZE = 15

# Base class for all solitaire boards.
class Board:
    name = "Board"

    def __init__(self, size=7):
        if not isinstance(size, int) or size % 2 == 0 \
                or size < MIN_SIZE or size > MAX_SIZE:
            raise ValueError(
                f"Board size must be an odd number from {MIN_SIZE} to {MAX_SIZE}.")
        self.size = size
        self.center = size // 2
        self.grid = []
        self.new_game()

    # Shape
    def is_on_board(self, row, col):
        raise NotImplementedError

    # Initial Setup
    def new_game(self):
        self.grid = [[PEG if self.is_on_board(r, c) else INVALID
                      for c in range(self.size)]
                     for r in range(self.size)]
        self.grid[self.center][self.center] = EMPTY

    # Queries
    def in_bounds(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def get_cell(self, row, col):
        if not self.in_bounds(row, col):
            return INVALID
        return self.grid[row][col]

    def peg_count(self):
        return sum(cell == PEG for row in self.grid for cell in row)

    # Making Move
    def get_move_error(self, from_row, from_col, to_row, to_col):
        if self.get_cell(from_row, from_col) != PEG:
            return "There is no peg in the starting hole."
        if self.get_cell(to_row, to_col) == INVALID:
            return "That location is off the board."
        if self.get_cell(to_row, to_col) == PEG:
            return "That hole is already occupied."
        dr, dc = to_row - from_row, to_col - from_col
        # Must move exactly two positions in one of 8 directions
        if abs(dr) not in (0, 2) or abs(dc) not in (0, 2):
            return "A peg must jump exactly two holes in a straight line."
        if self.get_cell(from_row + dr // 2, from_col + dc // 2) != PEG:
            return "There is no peg to jump over."
        return None

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        return self.get_move_error(from_row, from_col, to_row, to_col) is None

    def make_move(self, from_row, from_col, to_row, to_col):
        if not self.is_valid_move(from_row, from_col, to_row, to_col):
            return False
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        self.grid[from_row][from_col] = EMPTY
        self.grid[mid_row][mid_col] = EMPTY
        self.grid[to_row][to_col] = PEG
        return True

    # List of valid moves
    def get_valid_moves(self):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != PEG:
                    continue
                for dr, dc in DIRECTIONS:
                    tr, tc = r + 2 * dr, c + 2 * dc
                    if self.is_valid_move(r, c, tr, tc):
                        moves.append((r, c, tr, tc))
        return moves

    def is_game_over(self):
        return len(self.get_valid_moves()) == 0

    def get_rating(self):
        pegs = self.peg_count()
        if pegs == 1:
            return "Outstanding"
        if pegs == 2:
            return "Very Good"
        if pegs == 3:
            return "Good"
        return "Average"

class EnglishBoard(Board):
    name = "English"

    def is_on_board(self, row, col):
        corner = self.size // 3
        in_middle_rows = corner <= row < self.size - corner
        in_middle_cols = corner <= col < self.size - corner
        return in_middle_rows or in_middle_cols

class DiamondBoard(Board):
    name = "Diamond"

    def is_on_board(self, row, col):
        return abs(row - self.center) + abs(col - self.center) <= self.center

class HexagonBoard(Board):
    name = "Hexagon"

    def is_on_board(self, row, col):
        h = self.center
        flat = h // 2
        shrink = max(0, abs(row - h) - flat)
        return abs(col - h) <= h - shrink

BOARD_TYPES = {
    "English": EnglishBoard,
    "Hexagon": HexagonBoard,
    "Diamond": DiamondBoard,
}

DEFAULT_TYPE = "English"
DEFAULT_SIZE = 7

def create_board(board_type=DEFAULT_TYPE, size=DEFAULT_SIZE):
    if board_type not in BOARD_TYPES:
        raise ValueError(f"Unknown board type: {board_type}")
    return BOARD_TYPES[board_type](size)

# Main Class
class SolitaireGame:
    def __init__(self, board_type=DEFAULT_TYPE, size=DEFAULT_SIZE):
        self.board_type = board_type
        self.size = size
        self.board = None
        self.selected = None 
        self.move_count = 0
        self.is_over = False
        self.message = ""
        self.new_game()

    # Board Size
    def set_size(self, value):
        try:
            size = int(value)
            create_board(self.board_type, size)
        except (ValueError, TypeError):
            self.message = (f"Invalid board size. Use an odd number from "
                            f"{MIN_SIZE} to {MAX_SIZE}. Size stays at {self.size}.")
            return False
        self.size = size
        self.new_game()
        return True

    # Board Type
    def is_in_progress(self):
        return self.move_count > 0 and not self.is_over

    def set_board_type(self, board_type):
        if board_type not in BOARD_TYPES:
            self.message = f"Unknown board type: {board_type}"
            return False
        self.board_type = board_type
        self.new_game()
        return True

    # New Game
    def new_game(self):
        self.board = create_board(self.board_type, self.size)
        self.selected = None
        self.move_count = 0
        self.is_over = False
        self.message = f"New game: {self.board_type} board, size {self.size}."

    # Make Move
    def get_highlighted_destinations(self):
        """Empty holes the selected peg can jump to."""
        if self.selected is None:
            return []
        r, c = self.selected
        return [(tr, tc) for (fr, fc, tr, tc) in self.board.get_valid_moves()
                if (fr, fc) == (r, c)]

    def click(self, row, col):
        if self.is_over:
            self.message = "The game is over. Start a new game to keep playing."
            return False

        cell = self.board.get_cell(row, col)

        # Nothing selected yet: select a peg
        if self.selected is None:
            if cell == PEG:
                self.selected = (row, col)
                self.message = "Peg selected. Choose a highlighted hole."
            return False

        # Clicking the same peg again deselects it
        if (row, col) == self.selected:
            self.selected = None
            self.message = "Peg deselected."
            return False

        # Clicking a different peg selects that one instead
        if cell == PEG:
            self.selected = (row, col)
            self.message = "Peg selected. Choose a highlighted hole."
            return False

        # Clicking an empty area off the board deselects
        if cell == INVALID:
            self.selected = None
            self.message = "Peg deselected."
            return False

        # Otherwise try to move into the empty hole
        fr, fc = self.selected
        error = self.board.get_move_error(fr, fc, row, col)
        if error:
            self.message = f"Invalid move: {error}"
            return False

        self.board.make_move(fr, fc, row, col)
        self.selected = None
        self.move_count += 1
        self.check_game_over()
        return True

    # Game Over
    def check_game_over(self):
        pegs = self.board.peg_count()
        if self.board.is_game_over():
            self.is_over = True
            self.message = (f"Game over! Pegs left: {pegs}. "
                            f"Rating: {self.board.get_rating()}.")
        else:
            self.message = f"Pegs left: {pegs}."
        return self.is_over