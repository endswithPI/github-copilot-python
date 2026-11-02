"""Tests for Sudoku invariants that must hold before API work begins."""

import random
import unittest

import sudoku_logic


class SudokuLogicTests(unittest.TestCase):
    def test_conflicts_include_every_duplicate_cell(self) -> None:
        board = sudoku_logic.create_empty_board()
        board[0][0] = 4
        board[0][3] = 4
        board[3][0] = 4

        self.assertEqual(
            sudoku_logic.find_conflicts(board),
            {(0, 0), (0, 3), (3, 0)},
        )

    def test_invalid_board_shape_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "nine rows"):
            sudoku_logic.validate_board([[0]])

    def test_empty_board_has_at_least_two_solutions(self) -> None:
        self.assertEqual(sudoku_logic.count_solutions(sudoku_logic.create_empty_board()), 2)

    def test_generated_puzzles_have_configured_clues_and_one_solution(self) -> None:
        for index, difficulty in enumerate(sudoku_logic.DIFFICULTY_CLUES):
            with self.subTest(difficulty=difficulty):
                puzzle, solution = sudoku_logic.generate_puzzle(difficulty, random.Random(index + 7))

                clue_count = sum(value != sudoku_logic.EMPTY for row in puzzle for value in row)
                self.assertEqual(clue_count, sudoku_logic.DIFFICULTY_CLUES[difficulty])
                self.assertEqual(sudoku_logic.count_solutions(puzzle), 1)
                self.assertTrue(sudoku_logic.is_complete(solution))
                self.assertFalse(sudoku_logic.find_conflicts(solution))


if __name__ == "__main__":
    unittest.main()
