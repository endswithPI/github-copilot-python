"""Pure Sudoku board validation, solving, and unique-puzzle generation."""

from __future__ import annotations

import random
from collections.abc import Sequence

SIZE = 9
BOX_SIZE = 3
EMPTY = 0
DIFFICULTY_CLUES = {
    "easy": 45,
    "medium": 37,
    "hard": 31,
}

Board = list[list[int]]
Cell = tuple[int, int]


def create_empty_board() -> Board:
    """Return a new, empty 9 by 9 Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def copy_board(board: Board) -> Board:
    """Return a shallow-per-row copy so callers can safely mutate it."""
    return [row[:] for row in board]


def validate_board(board: object) -> Board:
    """Validate and return a Sudoku board containing only integer values 0..9."""
    if not isinstance(board, Sequence) or isinstance(board, (str, bytes)):
        raise ValueError("The board must contain nine rows of nine values.")
    if len(board) != SIZE:
        raise ValueError("The board must contain nine rows of nine values.")

    validated: Board = []
    for row in board:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes)) or len(row) != SIZE:
            raise ValueError("The board must contain nine rows of nine values.")
        validated_row: list[int] = []
        for value in row:
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= SIZE:
                raise ValueError("Each board value must be an integer between 0 and 9.")
            validated_row.append(value)
        validated.append(validated_row)
    return validated


def candidates_for(board: Board, row: int, col: int) -> list[int]:
    """Return digits that can be placed in an empty cell without a conflict."""
    if board[row][col] != EMPTY:
        return []

    used = set(board[row])
    used.update(board[index][col] for index in range(SIZE))
    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for row_offset in range(BOX_SIZE):
        for col_offset in range(BOX_SIZE):
            used.add(board[start_row + row_offset][start_col + col_offset])
    return [value for value in range(1, SIZE + 1) if value not in used]


def find_conflicts(board: Board) -> set[Cell]:
    """Return every non-empty cell involved in a row, column, or box duplicate."""
    conflicts: set[Cell] = set()

    def mark_duplicates(cells: list[Cell]) -> None:
        seen: dict[int, list[Cell]] = {}
        for row, col in cells:
            value = board[row][col]
            if value != EMPTY:
                seen.setdefault(value, []).append((row, col))
        for duplicate_cells in seen.values():
            if len(duplicate_cells) > 1:
                conflicts.update(duplicate_cells)

    for index in range(SIZE):
        mark_duplicates([(index, col) for col in range(SIZE)])
        mark_duplicates([(row, index) for row in range(SIZE)])
    for start_row in range(0, SIZE, BOX_SIZE):
        for start_col in range(0, SIZE, BOX_SIZE):
            mark_duplicates(
                [
                    (start_row + row_offset, start_col + col_offset)
                    for row_offset in range(BOX_SIZE)
                    for col_offset in range(BOX_SIZE)
                ]
            )
    return conflicts


def _next_empty_cell(board: Board) -> tuple[int, int, list[int]] | None:
    """Choose the empty cell with the fewest candidates to bound solver work."""
    best: tuple[int, int, list[int]] | None = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidates = candidates_for(board, row, col)
                if not candidates:
                    return row, col, []
                if best is None or len(candidates) < len(best[2]):
                    best = row, col, candidates
                    if len(candidates) == 1:
                        return best
    return best


def solve_board(board: Board, rng: random.Random | None = None) -> bool:
    """Solve ``board`` in place and return whether a solution was found."""
    next_cell = _next_empty_cell(board)
    if next_cell is None:
        return not find_conflicts(board)

    row, col, candidates = next_cell
    if not candidates:
        return False
    if rng is not None:
        rng.shuffle(candidates)

    for candidate in candidates:
        board[row][col] = candidate
        if solve_board(board, rng):
            return True
        board[row][col] = EMPTY
    return False


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count solutions up to ``limit`` without changing the caller's board."""
    if limit < 1:
        raise ValueError("The solution limit must be at least one.")

    working_board = copy_board(validate_board(board))
    if find_conflicts(working_board):
        return 0

    def search(found: int) -> int:
        if found >= limit:
            return found
        next_cell = _next_empty_cell(working_board)
        if next_cell is None:
            return found + 1

        row, col, candidates = next_cell
        for candidate in candidates:
            working_board[row][col] = candidate
            found = search(found)
            working_board[row][col] = EMPTY
            if found >= limit:
                break
        return found

    return search(0)


def is_complete(board: Board) -> bool:
    """Return whether every board cell contains a digit."""
    return all(value != EMPTY for row in board for value in row)


def _clue_target(difficulty: str | int) -> int:
    if isinstance(difficulty, bool):
        raise ValueError("Difficulty must be easy, medium, hard, or a clue count.")
    if isinstance(difficulty, int):
        if 0 <= difficulty <= SIZE * SIZE:
            return difficulty
        raise ValueError("Clue counts must be between 0 and 81.")
    try:
        return DIFFICULTY_CLUES[difficulty.lower()]
    except (AttributeError, KeyError) as error:
        raise ValueError("Difficulty must be easy, medium, or hard.") from error


def _carve_unique_puzzle(solution: Board, clue_target: int, rng: random.Random) -> Board | None:
    """Remove cells while retaining exactly one solution, or return ``None``."""
    puzzle = copy_board(solution)
    coordinates = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    rng.shuffle(coordinates)
    clues = SIZE * SIZE

    for row, col in coordinates:
        if clues <= clue_target:
            break
        value = puzzle[row][col]
        puzzle[row][col] = EMPTY
        if count_solutions(puzzle, limit=2) == 1:
            clues -= 1
        else:
            puzzle[row][col] = value

    return puzzle if clues == clue_target else None


def generate_puzzle(
    difficulty: str | int = "medium", rng: random.Random | None = None
) -> tuple[Board, Board]:
    """Generate a unique puzzle and its private solved board.

    Difficulty is intentionally defined by clue density for this application. The
    solution-count check is the invariant that ensures a puzzle remains fair.
    """
    clue_target = _clue_target(difficulty)
    generator = rng or random.Random()

    for _ in range(8):
        solution = create_empty_board()
        if not solve_board(solution, generator):
            continue
        puzzle = _carve_unique_puzzle(solution, clue_target, generator)
        if puzzle is not None:
            return puzzle, solution
    raise RuntimeError("Unable to generate a unique puzzle for this difficulty.")
