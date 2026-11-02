"""In-memory game storage for the local Flask application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from sudoku_logic import Board, Cell


@dataclass
class GameSession:
    """Server-side state for one generated game.

    This store is intentionally local and non-persistent. A production service
    would replace it with a session-aware persistent store.
    """

    game_id: str
    difficulty: str
    puzzle: Board
    solution: Board
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    hinted_cells: set[Cell] = field(default_factory=set)

    def public_puzzle(self) -> dict[str, object]:
        """Return only data that is safe to send to a browser."""
        clues = sum(value != 0 for row in self.puzzle for value in row)
        return {
            "gameId": self.game_id,
            "difficulty": self.difficulty,
            "puzzle": self.puzzle,
            "clues": clues,
        }


class GameNotFoundError(KeyError):
    """Raised when a request does not identify an active local game."""


class InMemoryGameStore:
    """Thread-safe, process-local store keyed by randomly generated game IDs."""

    def __init__(self) -> None:
        self._games: dict[str, GameSession] = {}
        self._lock = Lock()

    def create(self, difficulty: str, puzzle: Board, solution: Board) -> GameSession:
        """Create and store a new session without exposing its solution."""
        session = GameSession(str(uuid4()), difficulty, puzzle, solution)
        with self._lock:
            self._games[session.game_id] = session
        return session

    def get(self, game_id: str) -> GameSession:
        """Return a session or raise a domain-specific missing-game error."""
        with self._lock:
            try:
                return self._games[game_id]
            except KeyError as error:
                raise GameNotFoundError(game_id) from error
