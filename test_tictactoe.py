"""xUnit-style pytest tests for Pam Qian's Tic Tac Toe game.

Run with:  pytest -v test_tictactoe.py

xUnit style means the tests live in a class and use pytest's xUnit
fixtures (setup_class / setup_method / teardown_method) instead of
@pytest.fixture functions.
"""
import pathlib
import types
from unittest.mock import patch

GAME_FILE = pathlib.Path(__file__).with_name("tictactoe.py")


def load_game():
    """Load tictactoe.py without starting a game.

    The file calls main() at the bottom, which would block waiting for
    keyboard input on import. We read the source, drop that last call,
    and execute the rest into a fresh module object.
    """
    source = GAME_FILE.read_text()
    lines = [ln for ln in source.splitlines() if ln.strip() != "main()"]
    module = types.ModuleType("tictactoe")
    exec(compile("\n".join(lines), str(GAME_FILE), "exec"), module.__dict__)
    return module


class TestTicTacToe:
    # ---------- xUnit fixtures ----------
    @classmethod
    def setup_class(cls):
        """Runs once before all tests in this class."""
        cls.game = load_game()

    def setup_method(self, method):
        """Runs before every test: start from a fresh, empty board."""
        self.board = self.game.create_grid()
        self.p1, self.p2 = "X", "O"

    def teardown_method(self, method):
        """Runs after every test."""
        self.board = None

    # ---------- Test 1 ----------
    def test_isWinner_detects_three_in_a_row(self):
        """A full top row of X is a win, so isWinner returns False
        (in this program, False means 'game over, someone won')."""
        self.board[0] = ["X", "X", "X"]
        assert self.game.isWinner(self.board, self.p1, self.p2, 3) is False

        # And an empty board must NOT be reported as a win.
        empty = self.game.create_grid()
        assert self.game.isWinner(empty, self.p1, self.p2, 1) is True

    # ---------- Test 2 ----------
    def test_startGamming_places_symbol_and_rejects_filled_square(self):
        """Player 2 (odd count) picks (1,1), which is already taken, so the
        game must ask again; the second pick (2,0) should be used."""
        self.board[1][1] = "X"                       # square already filled
        answers = iter(["1", "1", "2", "0"])        # row, col, row, col

        with patch("builtins.input", lambda prompt="": next(answers)):
            result = self.game.startGamming(self.board, self.p1, self.p2, 1)

        assert result[2][0] == "O"   # new move landed in the free square
        assert result[1][1] == "X"   # existing mark was not overwritten
