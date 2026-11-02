# Sudoku Studio — Test Report

## Release under test

**Version:** v1.0.0  
**Test date:** 2 November 2026  
**Result:** **PASS — 22 automated tests passed**

## Test approach

Testing follows the incremental gates in [instruction.md](../instruction.md): validate the Sudoku domain first, then the game service, Flask contracts, and release-level acceptance criteria. Each automated test has a focused, brief purpose; browser checks cover interactive behaviour that is naturally visual or storage-backed.

| Layer | Tests | Brief description | Result |
| --- | ---: | --- | --- |
| Sudoku logic | 4 | Validates board shape, conflict identification, solution counting, and generated puzzle invariants. | Pass |
| Game service | 5 | Validates isolated games, hidden solutions, locked cells, hints, Check results, and completion. | Pass |
| Flask API | 4 | Validates public response shape and consistent errors for invalid input or missing games. | Pass |
| Release acceptance | 9 | Validates v1.0.0 visibility, functional rules, component separation, style contracts, persistence contract, documentation, and startup. | Pass |

Command executed:

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Acceptance coverage

| Acceptance criterion | Test / verification | Brief description | Status |
| --- | --- | --- | --- |
| Board has one unique solution | `test_every_difficulty_generates_a_unique_solvable_puzzle` | Counts solutions with an upper limit of two and requires exactly one for every difficulty. | Pass |
| Unique solvable generated puzzle | `test_generated_puzzles_have_configured_clues_and_one_solution` | Confirms each generated puzzle has a completed valid solution and one solution. | Pass |
| Easy, Medium, Hard change prefilled cells | `test_every_difficulty_generates_a_unique_solvable_puzzle` | Confirms 45, 37, and 31 clues and verifies the counts decrease by difficulty. | Pass |
| Prefilled cells are locked | `test_prefills_and_hints_are_locked_while_wrong_moves_are_reported` | Attempts to alter an original clue and expects a domain error. | Pass |
| Invalid moves give immediate feedback | `test_prefills_and_hints_are_locked_while_wrong_moves_are_reported`; browser check | Service identifies an incorrect move; client highlights row/column/box conflicts as the value is entered. | Pass |
| Completion congratulates player | `test_check_and_completion_contracts_support_player_feedback`; browser check | A correct full board reports `complete`; the UI reveals the congratulatory score panel. | Pass |
| Hint works and locks a valid cell | `test_prefills_and_hints_are_locked_while_wrong_moves_are_reported` | Requests a hint, then verifies the resulting hinted cell cannot be cleared. | Pass |
| Check works and highlights wrong values | `test_check_and_completion_contracts_support_player_feedback`; browser check | Check returns incorrect coordinates; the client maps them to invalid-cell styling. | Pass |
| Top 10 stores name, time, difficulty, hints | `test_top_ten_persistence_contract_is_present`; browser check | Validates the four score fields, browser storage reads/writes, ordering, and ten-item cap. | Pass |
| Top 10 persists between sessions | Browser reload check | A saved score remained after page reload through `localStorage`. | Pass |
| Timer works | Browser check | Timer advanced during play and stopped when the completed board was accepted. | Pass |
| Dark-mode toggle works | Browser reload check | The toggle applied the full dark theme and retained its selected state after reload. | Pass |
| Alternating 3×3 colours | `test_css_contract_covers_stable_responsive_light_and_dark_layout`; browser check | Confirms separate even/odd square selectors and verifies the board presentation. | Pass |
| No layout shifts from grid feedback | CSS acceptance contract; browser check | Uses border-box sizing, aspect-ratio, and reserved visual treatments while conflict states are applied. | Pass |
| Mobile and desktop adapt cleanly | CSS acceptance contract; browser check at 375 px | Uses Grid, media queries, and `clamp()`; mobile verification found no horizontal overflow. | Pass |
| Light/dark text and controls stay visible | CSS acceptance contract; browser check | Theme tokens and focus styles are present; buttons and labels remained legible in both modes. | Pass |
| Modular reusable components | `test_front_end_is_split_into_reusable_modules` | Requires separate API, board, state, timer, theme, leaderboard, and coordination modules. | Pass |
| Comments and consistent error handling | `test_core_modules_document_their_public_responsibilities`; `test_server_starts_and_uses_consistent_json_errors` | Checks documentation at public boundaries and a uniform JSON error envelope. | Pass |
| Code builds and runs | `test_server_starts_and_uses_consistent_json_errors` | Creates the Flask app and successfully serves the game route. | Pass |
| CSS approach used | `test_css_contract_covers_stable_responsive_light_and_dark_layout` | Confirms the application uses the selected plain-CSS approach. | Pass |
| Version is traceable | `test_release_version_is_visible_in_the_ui_and_api` | Confirms `v1.0.0` appears in the page and `/version` response. | Pass |

## Browser acceptance notes

The interactive player journey was exercised against the Flask application: start a game, enter a conflicting value, request a hint, use Check, solve a game, save a score, reload, switch themes, and inspect the mobile layout. These checks complement the automated Python suite; the application has no browser automation runtime dependency.

## Evidence and traceability

- Automated acceptance suite: [test_acceptance.py](../tests/test_acceptance.py)
- Regression suites: [test_sudoku_logic.py](../tests/test_sudoku_logic.py), [test_game_service.py](../tests/test_game_service.py), and [test_app.py](../tests/test_app.py)
- Release specification: [technical-specification.md](./technical-specification.md)
- Design diagrams: [uml.md](./uml.md)
