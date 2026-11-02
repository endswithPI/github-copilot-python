---
applyTo: "**"
---

# Sudoku Game Implementation Instructions

## Mission

Extend the existing Flask Sudoku application into a reliable, accessible, responsive game. Preserve the current Flask plus browser JavaScript approach unless a change is necessary for a stated requirement. Prefer small, cohesive, reusable modules over a large route handler or a large client script.

The application must support:

- Easy, Medium, and Hard difficulty levels.
- Generated puzzles with exactly one solvable solution.
- Locked prefilled cells and locked hint cells.
- Immediate visual feedback for invalid moves.
- Check and Hint actions.
- A completion message after a correct solution.
- A timer and a persistent local Top 10 list containing name, time, difficulty, and hints used.
- A light/dark theme toggle that updates the complete interface.
- Responsive and accessible desktop and mobile layouts.

## Working rules for the coding agent

1. Inspect the existing code before editing it. Preserve working behavior unless it conflicts with these requirements.
2. Implement one coherent feature at a time and keep the application runnable after each step.
3. Do not put business logic in Flask route functions or DOM event handlers. Routes and handlers should validate input, call a service, and format a response.
4. Do not expose the complete solution to the browser merely to implement hints or checking. Keep the authoritative solution on the server.
5. Do not use a global single-game object for user state. A generated game must have a game identifier and its state must be isolated from other games.
6. Do not rely on color alone to communicate errors, hints, focus, or completion.
7. Do not use `debug=True` as a production configuration.
8. Do not add a frontend framework or a CSS framework unless the existing requirements clearly justify the additional build and maintenance cost.
9. Add comments and docstrings for non-obvious decisions and public functions. Comments should explain why, not restate what the code does.
10. Keep the implementation compatible with the existing Python and Flask setup. Add dependencies only when they are justified and document them.

## Target module boundaries

The exact filenames may be adapted, but responsibilities should remain separate:

### Backend

- `app.py`: application creation, route registration, request parsing, and response formatting.
- `sudoku_logic.py`: board representation, validity checks, solving, solution counting, and puzzle generation.
- `game_service.py`: game creation, difficulty selection, hints, completion checks, and game lifecycle.
- `game_store.py`: per-game state storage. An in-memory store is acceptable for this local exercise, but it must be keyed by a game ID and documented as non-persistent server state.
- `errors.py`: consistent application exceptions and JSON error responses, if the implementation benefits from a separate module.

### Frontend

Keep `main.js` as a thin coordinator or split it into focused modules when useful:

- board rendering and cell state
- API client
- game state
- timer
- leaderboard/local storage
- theme management
- user feedback and accessibility announcements

Each module should expose a small public API and avoid mutating unrelated UI state.

## Backend behavior and contracts

Use explicit difficulty values: `easy`, `medium`, and `hard`. Reject unknown values with HTTP 400.

The following API shape is recommended:

### Create a game

`GET /new?difficulty=easy`

Return a response containing:

```json
{
  "gameId": "...",
  "difficulty": "easy",
  "puzzle": [[0, 0, 5,  ...]],
  "clues": 45
}
```

The exact clue counts may be tuned, but every difficulty must produce a valid puzzle with a different clue-density target.

### Request a hint

`POST /hint`

Request the `gameId` and current board. Return only one correct empty cell, for example:

```json
{
  "row": 2,
  "col": 7,
  "value": 4
}
```

Do not return the complete solution. Reject invalid game IDs, malformed boards, and requests for hints when no empty cell remains.

### Check a board

`POST /check`

Return separate information for:

- structural conflicts in the current board;
- incorrect non-empty user entries;
- whether the board is complete and solved.

Empty cells should not be reported as incorrect entries. The response should be safe for the client to render directly and should not reveal the full solution.

### Error format

Use one consistent JSON shape for expected errors, such as:

```json
{
  "error": {
    "code": "INVALID_BOARD",
    "message": "The board must contain nine rows of nine values."
  }
}
```

Use appropriate status codes: 400 for malformed input, 404 for an unknown game, 409 for a valid request that conflicts with game state, and 500 for unexpected failures. Add Flask error handlers so users receive a useful message rather than a traceback.

## Sudoku generation requirements

1. Generate a complete valid board using a backtracking solver.
2. Remove candidate cells one at a time.
3. After each tentative removal, count solutions with an early exit after two solutions are found.
4. Keep the removal only when exactly one solution remains.
5. Stop at the configured clue target for the selected difficulty.
6. Validate the final puzzle before returning it.

Do not equate difficulty with clue count without documenting that this is a first approximation. The important invariant is that every puzzle has exactly one solution.

## Frontend behavior

### Board and moves

- Render the board from state rather than duplicating cell markup.
- Use event delegation for cell input and selection where practical.
- Prefilled cells must be disabled or otherwise impossible to edit through the normal UI.
- Hint cells must be locked after insertion and visually distinct from original clues.
- On each user entry, detect duplicate values in the same row, column, or 3×3 box.
- Mark conflicts with `aria-invalid`, visible styling, and an accessible message. Never rely on color alone.
- Do not mark empty cells as incorrect during Check.

### Completion

When the board is full, submit it for authoritative server validation. Only after the server confirms success should the UI:

- stop the timer;
- show a congratulatory message;
- offer a name entry for the score;
- update the Top 10 list.

### Timer

- Start when a puzzle is successfully created.
- Reset on New Game or a difficulty change.
- Calculate elapsed time from timestamps rather than counting interval callbacks.
- Stop exactly once after successful completion.
- Keep the displayed time readable on small screens.

### Top 10 persistence

Store the list in a versioned key such as `sudoku.leaderboard.v1`. Each entry should include:

```json
{
  "name": "Player",
  "timeSeconds": 248,
  "difficulty": "medium",
  "hintsUsed": 1,
  "createdAt": "2026-11-01T12:00:00.000Z"
}
```

Sort by fastest time, retain only ten entries, and gracefully recover from invalid or unavailable local storage. Render player names with `textContent`, not HTML interpolation.

Local storage is intentionally a personal, browser-local leaderboard. Do not describe it as a secure or shared competition ranking.

### Theme

- Use CSS custom properties for all page, surface, text, border, cell, control, feedback, and focus colors.
- Support light and dark themes through a root `data-theme` attribute or class.
- Initialize from the saved user preference, falling back to `prefers-color-scheme`.
- Persist the selected theme in local storage.
- Verify contrast and visibility for text, controls, clues, hints, errors, success messages, and focus indicators in both themes.

## Layout and accessibility

Use plain CSS unless a framework is demonstrably useful for this small Flask application.

- Use CSS Grid for the 9×9 board.
- Use responsive sizing such as `min()`, `max()`, `clamp()`, and `aspect-ratio`; avoid a fixed desktop-only cell size.
- Keep board dimensions stable when a cell changes state. Background, border, and text changes must not cause layout shifts.
- Give the 3×3 regions alternating colors using stable region classes or data attributes.
- Preserve strong 3×3 boundaries without changing cell dimensions.
- Add a mobile viewport declaration.
- Keep buttons and inputs touch-friendly.
- Provide visible `:focus-visible` styles.
- Use semantic labels, useful button names, appropriate input modes, and an `aria-live` region for status messages.
- Make all important information available without depending on color.
- Test narrow mobile widths and a wide desktop layout.

## Incremental delivery and verification gates

Implement and validate the application in this order:

1. Establish a runnable baseline and a test harness.
2. Build and test Sudoku validation, solving, and unique-solution generation.
3. Build and test isolated game state plus Flask API contracts.
4. Build and test board rendering, locked cells, and immediate conflict feedback.
5. Build and test difficulty, Hint, Check, and completion behavior together.
6. Build and test the timer, theme persistence, and Top 10 local storage behavior.
7. Validate responsive, light, dark, keyboard, and mobile experiences.

Do not begin the next increment until the current increment passes all of these gates:

- focused tests for the changed behavior pass;
- the full test suite passes;
- editor diagnostics and browser-console errors are resolved;
- one representative player journey succeeds manually;
- prior completed behavior has a regression check;
- every discovered defect is fixed and retested.

Maintain a simple requirement-to-test checklist so every requested feature has an implementation location and a verification scenario.

## Testing expectations

Add tests before declaring the work complete. At minimum cover:

- valid completed boards;
- invalid rows, columns, and 3×3 regions;
- solver correctness;
- solution counting, including rejecting puzzles with multiple solutions;
- difficulty clue targets;
- locked prefilled and hint cells;
- malformed API requests;
- unknown game IDs;
- hint behavior;
- successful and unsuccessful checks;
- leaderboard sorting, trimming, and persistence recovery.

If browser automation is not available, keep DOM-facing logic small and test pure functions separately. Do not claim responsive or accessibility support without manually checking representative desktop, mobile, light, and dark layouts.

## Definition of done

The implementation is complete only when:

- every generated puzzle is solvable and has exactly one solution;
- all three difficulty levels work and affect clue density;
- clues and hints are locked;
- invalid moves receive immediate, accessible feedback;
- Check, Hint, completion, timer, theme, and Top 10 behavior work together;
- Top 10 data survives refreshes and reopening the app;
- API failures are handled consistently and visibly;
- the UI has no avoidable layout shifts at tested viewport sizes;
- light and dark themes keep text and controls readable;
- automated tests cover the core invariants;
- the README documents how to run and use the completed game.

See [`docs/uml.md`](docs/uml.md) for the target component, interaction, state, and domain diagrams.
