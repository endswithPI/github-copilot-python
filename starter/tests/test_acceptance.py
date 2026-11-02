"""Release-level acceptance tests for the Sudoku Studio user requirements."""

from __future__ import annotations

from pathlib import Path
import random
import unittest

from app import GAME_VERSION, create_app
from game_service import GameService
from game_store import InMemoryGameStore
import sudoku_logic
from test_game_service import SOLUTION, copy_board, fixed_puzzle


STARTER_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = STARTER_ROOT / "static"


class AcceptanceTests(unittest.TestCase):
    """Validate the versioned game against its externally visible requirements."""

    def setUp(self) -> None:
        self.service = GameService(InMemoryGameStore(), fixed_puzzle, random.Random(11))
        self.client = create_app(self.service).test_client()

    def test_release_version_is_visible_in_the_ui_and_api(self) -> None:
        """Players and test tooling can identify the exact release being exercised."""
        page = self.client.get("/")
        version = self.client.get("/version")

        self.assertEqual(page.status_code, 200)
        self.assertIn(f"Sudoku Studio v{GAME_VERSION}", page.get_data(as_text=True))
        self.assertEqual(version.get_json(), {"version": GAME_VERSION})

    def test_every_difficulty_generates_a_unique_solvable_puzzle(self) -> None:
        """Easy, Medium, and Hard use their configured clue counts and one solution."""
        clue_counts = []
        for index, difficulty in enumerate(("easy", "medium", "hard")):
            with self.subTest(difficulty=difficulty):
                puzzle, solution = sudoku_logic.generate_puzzle(difficulty, random.Random(index + 100))
                clues = sum(value != sudoku_logic.EMPTY for row in puzzle for value in row)
                clue_counts.append(clues)
                self.assertEqual(clues, sudoku_logic.DIFFICULTY_CLUES[difficulty])
                self.assertEqual(sudoku_logic.count_solutions(puzzle), 1)
                self.assertTrue(sudoku_logic.is_complete(solution))

        self.assertGreater(clue_counts[0], clue_counts[1])
        self.assertGreater(clue_counts[1], clue_counts[2])

    def test_prefills_and_hints_are_locked_while_wrong_moves_are_reported(self) -> None:
        """The game prevents edits to locked cells and returns immediate move feedback."""
        game = self.service.create_game("easy")
        board = copy_board(game.puzzle)
        board[0][0] = 4
        feedback = self.service.check_game(game.game_id, board)
        self.assertIn([0, 0], feedback["incorrect"])

        hint = self.service.request_hint(game.game_id, copy_board(game.puzzle))
        board = copy_board(game.puzzle)
        board[hint["row"]][hint["col"]] = 0
        with self.assertRaisesRegex(Exception, "Hinted cells"):
            self.service.check_game(game.game_id, board)

        board = copy_board(game.puzzle)
        board[0][1] = 1
        with self.assertRaisesRegex(Exception, "Prefilled cells"):
            self.service.check_game(game.game_id, board)

    def test_check_and_completion_contracts_support_player_feedback(self) -> None:
        """Check identifies only incorrect entries and a solved board completes."""
        game = self.service.create_game("easy")
        board = copy_board(game.puzzle)
        board[0][0] = 4

        checked = self.service.check_game(game.game_id, board)
        self.assertEqual(checked["incorrect"], [[0, 0]])
        self.assertFalse(checked["complete"])

        solved = self.service.check_game(game.game_id, copy_board(SOLUTION))
        self.assertTrue(solved["complete"])
        self.assertFalse(solved["incorrect"])
        self.assertFalse(solved["conflicts"])

    def test_top_ten_persistence_contract_is_present(self) -> None:
        """The browser leaderboard saves validated scores and retains only ten entries."""
        source = (STATIC_ROOT / "leaderboard.js").read_text(encoding="utf-8")

        self.assertIn('"sudoku.leaderboard.v1"', source)
        self.assertIn("localStorage.setItem", source)
        self.assertIn("localStorage.getItem", source)
        self.assertIn(".slice(0, 10)", source)
        for field in ("name", "timeSeconds", "difficulty", "hintsUsed"):
            self.assertIn(field, source)

    def test_front_end_is_split_into_reusable_modules(self) -> None:
        """The board, timer, theme, leaderboard, state, and API use separate modules."""
        expected_modules = {
            "api.js",
            "board.js",
            "game-state.js",
            "leaderboard.js",
            "main.js",
            "theme.js",
            "timer.js",
        }
        self.assertTrue(expected_modules.issubset({path.name for path in STATIC_ROOT.glob("*.js")}))
        main_source = (STATIC_ROOT / "main.js").read_text(encoding="utf-8")
        self.assertGreaterEqual(main_source.count(" from \"./"), 6)

    def test_css_contract_covers_stable_responsive_light_and_dark_layout(self) -> None:
        """Styles declare alternating boxes, responsive sizing, and accessible themes."""
        source = (STATIC_ROOT / "styles.css").read_text(encoding="utf-8")

        for rule in (
            ".box-even",
            ".box-odd",
            "box-sizing: border-box",
            "aspect-ratio:",
            "@media",
            "clamp(",
            ':root[data-theme="dark"]',
            ":focus-visible",
        ):
            self.assertIn(rule, source)

    def test_server_starts_and_uses_consistent_json_errors(self) -> None:
        """The Flask app serves the page and normalises expected client errors."""
        page = self.client.get("/")
        invalid_difficulty = self.client.get("/new?difficulty=impossible")
        invalid_body = self.client.post("/check", data="not-json", content_type="text/plain")

        self.assertEqual(page.status_code, 200)
        for response, code in ((invalid_difficulty, "INVALID_DIFFICULTY"), (invalid_body, "INVALID_JSON")):
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json()["error"]["code"], code)
            self.assertIn("message", response.get_json()["error"])

    def test_core_modules_document_their_public_responsibilities(self) -> None:
        """Maintainability safeguards include module and service documentation."""
        self.assertTrue(sudoku_logic.__doc__)
        self.assertTrue(GameService.__doc__)
        self.assertIn("injectable", create_app.__doc__)


if __name__ == "__main__":
    unittest.main()
