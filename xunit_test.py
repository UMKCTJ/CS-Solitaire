import unittest

from logic import (EMPTY, INVALID, PEG, DiamondBoard, EnglishBoard,
                             HexagonBoard, SolitaireGame, create_board)

# For test to place its own pegs
def clear_board(board):
    for r in range(board.size):
        for c in range(board.size):
            if board.grid[r][c] != INVALID:
                board.grid[r][c] = EMPTY

# Board Size (User Story #1)
class TestBoardSize(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame("English", 7)

    def valid_size_changes_board(self):
        self.assertTrue(self.game.set_size("9"))
        self.assertEqual(self.game.size, 9)
        self.assertEqual(self.game.board.size, 9)

    def invalid_number_reverts_to_previous_size(self):
        for bad in ("4", "3", "17"):
            self.assertFalse(self.game.set_size(bad))
            self.assertEqual(self.game.size, 7)
            self.assertEqual(self.game.board.size, 7)

    def invalid_character_reverts_to_previous_size(self):
        for bad in ("abc", "", "7.5"):
            self.assertFalse(self.game.set_size(bad))
            self.assertEqual(self.game.size, 7)

# Board Type
class TestBoardType(unittest.TestCase):
    def selecting_type_layout(self):
        game = SolitaireGame("English", 7)
        game.set_board_type("Diamond")
        self.assertIsInstance(game.board, DiamondBoard)
        game.set_board_type("Hexagon")
        self.assertIsInstance(game.board, HexagonBoard)

    def english_board_has_correct_holes_pegs_and_empty_center(self):
        board = create_board("English", 7)
        holes = sum(cell != INVALID for row in board.grid for cell in row)
        self.assertEqual(holes, 33)
        self.assertEqual(board.peg_count(), 32)
        self.assertEqual(board.get_cell(3, 3), EMPTY)
        for r, c in [(0, 0), (0, 6), (6, 0), (6, 6)]:
            self.assertEqual(board.get_cell(r, c), INVALID)

    def diamond_board_has_correct_holes_and_empty_center(self):
        board = create_board("Diamond", 7)
        holes = sum(cell != INVALID for row in board.grid for cell in row)
        self.assertEqual(holes, 25)
        self.assertEqual(board.peg_count(), 24)
        self.assertEqual(board.get_cell(3, 3), EMPTY)

    def default_type_is_english_and_player_is_told(self):
        game = SolitaireGame()
        self.assertEqual(game.board_type, "English")
        self.assertIsInstance(game.board, EnglishBoard)
        self.assertIn("English", game.message)

    def game_in_progress_needs_confirmation(self):
        game = SolitaireGame("English", 7)
        self.assertFalse(game.is_in_progress())      # no moves yet: no prompt
        game.click(1, 3)
        game.click(3, 3)                             # make one move
        self.assertTrue(game.is_in_progress())       # GUI must now ask to confirm

# Start a new game (User Story #2)
class TestStartNewGame(unittest.TestCase):
    def new_game_uses_chosen_size_and_type(self):
        game = SolitaireGame("Hexagon", 9)
        self.assertIsInstance(game.board, HexagonBoard)
        self.assertEqual(game.board.size, 9)
        self.assertEqual(game.move_count, 0)
        self.assertFalse(game.is_over)

    def new_game_again_wipes_the_board(self):
        game = SolitaireGame("English", 7)
        game.click(1, 3)
        game.click(3, 3)
        self.assertEqual(game.board.peg_count(), 31)
        game.new_game()
        self.assertEqual(game.board.peg_count(), 32)
        self.assertEqual(game.board.get_cell(3, 3), EMPTY)
        self.assertEqual(game.move_count, 0)
        self.assertIsNone(game.selected)

# Making move (User Story #3)
class TestMakeMove(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame("English", 7)

    def valid_move_jumps_and_removes_peg(self):
        self.game.click(1, 3)                         # select peg
        self.assertIn((3, 3), self.game.get_highlighted_destinations())
        self.assertTrue(self.game.click(3, 3))        # jump down over (2,3)
        board = self.game.board
        self.assertEqual(board.get_cell(1, 3), EMPTY)
        self.assertEqual(board.get_cell(2, 3), EMPTY)
        self.assertEqual(board.get_cell(3, 3), PEG)
        self.assertEqual(board.peg_count(), 31)
        self.assertIn("31", self.game.message)       # peg count shown

    def valid_diagonal_move(self):
        game = SolitaireGame("Diamond", 9)
        game.click(2, 2)
        self.assertTrue(game.click(4, 4))
        self.assertEqual(game.board.get_cell(3, 3), EMPTY)

    def jump_over_empty_hole_is_rejected_with_reason(self):
        self.game.click(1, 3)
        self.game.click(3, 3)                         # now (1,3) and (2,3) empty
        self.game.click(0, 3)                         # select top peg
        self.assertFalse(self.game.click(2, 3))       # nothing to jump over
        self.assertIn("no peg to jump over", self.game.message)
        self.assertEqual(self.game.board.peg_count(), 31)

    def wrong_distance_is_rejected_with_reason(self):
        self.game.click(0, 3)
        self.assertFalse(self.game.click(3, 3))       # three holes away
        self.assertIn("exactly two holes", self.game.message)
        self.assertEqual(self.game.board.peg_count(), 32)

    def off_board_and_occupied_are_rejected(self):
        board = self.game.board
        self.assertEqual(board.get_move_error(2, 2, 0, 0),
                         "That location is off the board.")
        self.assertEqual(board.get_move_error(2, 3, 4, 3),
                         "That hole is already occupied.")
        self.assertEqual(board.peg_count(), 32)

    def clicking_same_peg_deselects(self):
        self.game.click(1, 3)
        self.assertEqual(self.game.selected, (1, 3))
        self.game.click(1, 3)
        self.assertIsNone(self.game.selected)
        self.assertEqual(self.game.get_highlighted_destinations(), [])

    def clicking_empty_area_deselects(self):
        self.game.click(1, 3)
        self.game.click(0, 0)                         # corner: not on the board
        self.assertIsNone(self.game.selected)
        self.assertEqual(self.game.get_highlighted_destinations(), [])

    def game_ends_after_last_possible_move(self):
        clear_board(self.game.board)
        self.game.board.grid[3][2] = PEG
        self.game.board.grid[3][3] = PEG
        self.game.click(3, 2)
        self.game.click(3, 4)                         # only move left
        self.assertTrue(self.game.is_over)
        self.assertIn("Game over", self.game.message)

# Game over (User Story #4)
class TestGameOver(unittest.TestCase):
    def setUp(self):
        self.game = SolitaireGame("English", 7)
        clear_board(self.game.board)

    def new_game_is_not_over(self):
        self.assertFalse(SolitaireGame().board.is_game_over())

    def one_marble_left_is_game_over(self):
        self.game.board.grid[3][3] = PEG
        self.assertTrue(self.game.check_game_over())

    def no_valid_moves_is_game_over(self):
        self.game.board.grid[0][2] = PEG
        self.game.board.grid[6][4] = PEG
        self.assertTrue(self.game.check_game_over())

    def actions_rejected_after_game_over(self):
        self.game.board.grid[0][2] = PEG
        self.game.board.grid[6][4] = PEG
        self.game.check_game_over()
        self.assertFalse(self.game.click(0, 2))
        self.assertIsNone(self.game.selected)
        self.assertIn("Start a new game", self.game.message)
        self.game.new_game()                          # new game allows play again
        self.assertFalse(self.game.is_over)

if __name__ == "__main__":
    unittest.main()