"""Flask endpoint contract tests."""

import unittest

from app import create_app
from game_service import GameService
from game_store import InMemoryGameStore
from test_game_service import fixed_puzzle


class AppTests(unittest.TestCase):
    def setUp(self) -> None:
        service = GameService(InMemoryGameStore(), fixed_puzzle)
        self.client = create_app(service).test_client()

    def test_new_game_returns_public_game_data(self) -> None:
        response = self.client.get("/new?difficulty=medium")

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["difficulty"], "medium")
        self.assertIn("gameId", payload)
        self.assertNotIn("solution", payload)

    def test_new_game_rejects_unknown_difficulty(self) -> None:
        response = self.client.get("/new?difficulty=expert")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "INVALID_DIFFICULTY")

    def test_check_rejects_non_json_data(self) -> None:
        response = self.client.post("/check", data="not json", content_type="text/plain")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "INVALID_JSON")

    def test_hint_rejects_unknown_game(self) -> None:
        response = self.client.post("/hint", json={"gameId": "missing", "board": [[0] * 9 for _ in range(9)]})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"]["code"], "GAME_NOT_FOUND")
