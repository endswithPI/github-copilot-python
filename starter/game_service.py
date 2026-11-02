"""Application service for Sudoku game creation, hints, and validation."""

from __future__ import annotations

import random
from collections.abc import Callable

import sudoku_logic
from game_store import GameNotFoundError, GameSession, InMemoryGameStore


class GameError(Exception):
    """An expected domain error that can be converted into a JSON response."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


PuzzleGenerator = Callable[[str], tuple[sudoku_logic.Board, sudoku_logic.Board]]


class GameService:
    """Coordinate Sudoku logic with per-game state and API-safe results."""

    def __init__(
        self,
        store: InMemoryGameStore | None = None,
        puzzle_generator: PuzzleGenerator = sudoku_logic.generate_puzzle,
        rng: random.Random | None = None,
    ) -> None:
        self._store = store or InMemoryGameStore()
        self._puzzle_generator = puzzle_generator
        self._rng = rng or random.Random()

    def create_game(self, difficulty: object) -> GameSession:
        """Generate and persist a new game after validating its difficulty."""
        if not isinstance(difficulty, str) or difficulty.lower() not in sudoku_logic.DIFFICULTY_CLUES:
            raise GameError(400, "INVALID_DIFFICULTY", "Choose Easy, Medium, or Hard.")
        normalized_difficulty = difficulty.lower()
        try:
            puzzle, solution = self._puzzle_generator(normalized_difficulty)
        except RuntimeError as error:
            raise GameError(500, "GENERATION_FAILED", "A puzzle could not be generated. Please try again.") from error
        return self._store.create(normalized_difficulty, puzzle, solution)

    def request_hint(self, game_id: object, board: object) -> dict[str, int]:
        """Return one solution value for a currently empty, editable cell."""
        session, current_board = self._session_and_board(game_id, board)
        empty_cells = [
            (row, col)
            for row in range(sudoku_logic.SIZE)
            for col in range(sudoku_logic.SIZE)
            if current_board[row][col] == sudoku_logic.EMPTY
        ]
        if not empty_cells:
            raise GameError(409, "NO_HINT_AVAILABLE", "There are no empty cells left to fill.")

        row, col = self._rng.choice(empty_cells)
        session.hinted_cells.add((row, col))
        return {"row": row, "col": col, "value": session.solution[row][col]}

    def check_game(self, game_id: object, board: object) -> dict[str, object]:
        """Return safe conflict and correctness information for the submitted board."""
        session, current_board = self._session_and_board(game_id, board)
        conflicts = sorted(sudoku_logic.find_conflicts(current_board))
        incorrect = [
            [row, col]
            for row in range(sudoku_logic.SIZE)
            for col in range(sudoku_logic.SIZE)
            if current_board[row][col] != sudoku_logic.EMPTY
            and current_board[row][col] != session.solution[row][col]
        ]
        complete = (
            sudoku_logic.is_complete(current_board)
            and not conflicts
            and not incorrect
        )
        return {
            "conflicts": [list(cell) for cell in conflicts],
            "incorrect": incorrect,
            "complete": complete,
        }

    def _session_and_board(self, game_id: object, board: object) -> tuple[GameSession, sudoku_logic.Board]:
        """Validate request data and keep original clues and hints immutable."""
        if not isinstance(game_id, str) or not game_id:
            raise GameError(400, "INVALID_GAME_ID", "A valid game ID is required.")
        try:
            session = self._store.get(game_id)
        except GameNotFoundError as error:
            raise GameError(404, "GAME_NOT_FOUND", "This game is no longer available. Start a new game.") from error
        try:
            current_board = sudoku_logic.validate_board(board)
        except ValueError as error:
            raise GameError(400, "INVALID_BOARD", str(error)) from error

        for row in range(sudoku_logic.SIZE):
            for col in range(sudoku_logic.SIZE):
                original_value = session.puzzle[row][col]
                if original_value and current_board[row][col] != original_value:
                    raise GameError(409, "IMMUTABLE_CLUE", "Prefilled cells cannot be changed.")
                if (row, col) in session.hinted_cells and current_board[row][col] != session.solution[row][col]:
                    raise GameError(409, "IMMUTABLE_HINT", "Hinted cells cannot be changed.")
        return session, current_board
