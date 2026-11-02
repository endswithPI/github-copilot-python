"""Flask entry point for the Sudoku game."""

from __future__ import annotations

import logging

from flask import Flask, jsonify, render_template, request

from game_service import GameError, GameService

GAME_VERSION = "1.0.0"


def create_app(game_service: GameService | None = None) -> Flask:
    """Create the app with injectable services so endpoint tests stay isolated."""
    app = Flask(__name__)
    app.config["GAME_SERVICE"] = game_service or GameService()

    @app.errorhandler(GameError)
    def handle_game_error(error: GameError):
        return jsonify({"error": {"code": error.code, "message": error.message}}), error.status

    @app.errorhandler(500)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected Sudoku application error", exc_info=error)
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": "Something went wrong. Please try again."}}), 500

    @app.get("/")
    def index():
        return render_template("index.html", version=GAME_VERSION)

    @app.get("/version")
    def version():
        """Expose the running release for operational and acceptance checks."""
        return jsonify({"version": GAME_VERSION})

    @app.route("/new", methods=["GET", "POST"])
    def new_game():
        payload = _optional_json_payload()
        difficulty = payload.get("difficulty", request.args.get("difficulty", "medium"))
        game = _game_service().create_game(difficulty)
        return jsonify(game.public_puzzle()), 201

    @app.post("/hint")
    def hint():
        payload = _required_json_payload()
        return jsonify(_game_service().request_hint(payload.get("gameId"), payload.get("board")))

    @app.post("/check")
    def check_solution():
        payload = _required_json_payload()
        return jsonify(_game_service().check_game(payload.get("gameId"), payload.get("board")))

    def _game_service() -> GameService:
        return app.config["GAME_SERVICE"]

    def _optional_json_payload() -> dict[str, object]:
        if not request.data:
            return {}
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise GameError(400, "INVALID_JSON", "The request body must be a JSON object.")
        return payload

    def _required_json_payload() -> dict[str, object]:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise GameError(400, "INVALID_JSON", "The request body must be a JSON object.")
        return payload

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run()
