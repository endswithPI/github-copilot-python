# Sudoku Studio — Technical Specification

## Release

**Version:** v1.0.0  
**Application:** Sudoku Studio  
**Runtime:** Python/Flask with a browser-native JavaScript interface

## Product scope

Sudoku Studio is a responsive, accessible nine-by-nine Sudoku game. It generates an Easy, Medium, or Hard puzzle with exactly one solution, gives immediate move feedback, and records completed-game scores locally in the player’s browser.

## Architecture

- `app.py` owns Flask app creation, routes, version exposure, and the uniform JSON error envelope.
- `sudoku_logic.py` owns board validation, conflict detection, solving, solution counting, and unique-puzzle generation.
- `game_store.py` owns isolated in-memory game sessions.
- `game_service.py` owns gameplay rules: prefilled/hinted locking, hints, checking, and completion results.
- `static/` splits the client into API, board, game-state, timer, theme, leaderboard, and coordination modules.
- `templates/index.html` contains the semantic, keyboard-accessible application shell; `static/styles.css` provides responsive plain CSS.

The component, sequence, state, and domain views are maintained in [uml.md](./uml.md).

## Functional behaviour

| Requirement | v1.0.0 behaviour |
| --- | --- |
| Unique puzzles | The generator removes clues only when `count_solutions(..., limit=2)` remains one. |
| Difficulty | Easy/Medium/Hard have 45/37/31 given cells respectively. |
| Cell safety | Original clues and server-issued hints cannot be changed. |
| Immediate feedback | Client conflict detection marks duplicate row, column, or 3×3-square entries; **Check** also compares entries to the solution. |
| Hints and completion | **Hint** fills and locks a correct empty cell. A complete correct board opens a congratulatory panel. |
| Timer and scores | The timer starts with a new game and stops at completion. Scores contain player name, elapsed seconds, difficulty, and hints used. |
| Top 10 persistence | `localStorage` key `sudoku.leaderboard.v1` keeps the fastest ten scores between browser sessions. |
| Theme | The dark-mode toggle persists the selected theme and applies it to the full UI. |

## Interface and quality attributes

- Plain CSS uses theme tokens, `clamp()` sizing, CSS Grid, media queries, and `aspect-ratio` to adapt from mobile to desktop.
- Alternating `box-even` and `box-odd` regions distinguish 3×3 squares. Border-box sizing and fixed error insets prevent movement when feedback appears.
- Form controls have visible focus states, labelled controls, a live status message, and sufficient theme-specific text/control styling.
- Expected client failures return `{ "error": { "code": "…", "message": "…" } }`; client modules display those messages without breaking the active game.
- Python modules use docstrings and narrow responsibilities; browser modules isolate reusable UI and persistence behaviour.

## HTTP contract

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Serves the game UI, including the running version. |
| `/version` | GET | Returns `{ "version": "1.0.0" }`. |
| `/new` | GET/POST | Starts a game for `easy`, `medium`, or `hard`. |
| `/hint` | POST | Returns one correct, locked cell for the supplied game and board. |
| `/check` | POST | Returns conflicts, incorrect values, and completion state. |

## Verification baseline

Release v1.0.0 is verified by the unit, endpoint, and acceptance suites in `tests/`. The detailed results and brief descriptions are recorded in [test-report.md](./test-report.md).

## Deliberate boundaries

- Scores are private to the current browser; no account or server database is required.
- Active game sessions are in memory, so restarting the Flask process starts fresh games.
