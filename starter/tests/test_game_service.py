"""Tests for game-session isolation, hints, and safe validation results."""

import random
import unittest

from game_service import GameError, GameService
from game_store import InMemoryGameStore


SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def copy_board(board):
    return [row[:] for row in board]


def fixed_puzzle(difficulty: str):
    puzzle = copy_board(SOLUTION)
    puzzle[0][0] = 0
    puzzle[1][1] = 0
    return puzzle, copy_board(SOLUTION)


class GameServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = GameService(
            store=InMemoryGameStore(),
            puzzle_generator=fixed_puzzle,
            rng=random.Random(1),
        )
        self.game = self.service.create_game("easy")

    def test_public_game_never_contains_solution(self) -> None:
        public_game = self.game.public_puzzle()

        self.assertIn("gameId", public_game)
        self.assertNotIn("solution", public_game)
        self.assertEqual(public_game["difficulty"], "easy")

    def test_hint_fills_an_empty_cell_and_then_locks_it(self) -> None:
        board = copy_board(self.game.puzzle)
        hint = self.service.request_hint(self.game.game_id, board)
        board[hint["row"]][hint["col"]] = hint["value"]

        result = self.service.check_game(self.game.game_id, board)
        self.assertFalse(result["incorrect"])

        board[hint["row"]][hint["col"]] = 0
        with self.assertRaisesRegex(GameError, "Hinted cells"):
            self.service.check_game(self.game.game_id, board)

    def test_check_ignores_empty_cells_and_reports_wrong_entries(self) -> None:
        board = copy_board(self.game.puzzle)
        board[0][0] = 4

        result = self.service.check_game(self.game.game_id, board)

        self.assertIn([0, 0], result["incorrect"])
        self.assertNotIn([1, 1], result["incorrect"])
        self.assertFalse(result["complete"])

    def test_prefilled_cells_cannot_be_changed(self) -> None:
        board = copy_board(self.game.puzzle)
        board[0][1] = 1

        with self.assertRaisesRegex(GameError, "Prefilled cells"):
            self.service.check_game(self.game.game_id, board)

    def test_complete_correct_board_is_reported_as_complete(self) -> None:
        result = self.service.check_game(self.game.game_id, copy_board(SOLUTION))

        self.assertTrue(result["complete"])
        self.assertFalse(result["conflicts"])
        self.assertFalse(result["incorrect"])
