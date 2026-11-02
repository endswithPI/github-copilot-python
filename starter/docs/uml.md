# Sudoku Game UML Views

These diagrams describe the target design for the implementation. They are intentionally technology-light: the exact Python module names and browser module names may evolve, but the responsibilities and boundaries should remain recognizable.

## 1. Component and deployment view

```mermaid
flowchart LR
    Player((Player))

    subgraph Browser[Browser]
        UI[Game UI]
        Board[Board Renderer]
        Timer[Timer]
        Theme[Theme Manager]
        Scores[Leaderboard Manager]
        Storage[(localStorage)]
    end

    subgraph Flask[Flask Application]
        Routes[HTTP Routes]
        Service[Game Service]
        Logic[Sudoku Logic]
        Store[(Game Store)]
    end

    Player --> UI
    UI --> Board
    UI --> Timer
    UI --> Theme
    UI --> Scores
    Scores <--> Storage
    Theme <--> Storage
    UI --> Routes
    Routes --> Service
    Service --> Logic
    Service <--> Store
    Routes --> UI
```

The browser owns presentation, timer display, theme preference, and the personal leaderboard. Flask owns puzzle validity, solution uniqueness, game state, hints, and authoritative completion checks.

## 2. New game, hint, check, and completion sequence

```mermaid
sequenceDiagram
    actor Player
    participant UI as Game UI
    participant API as Flask API
    participant Service as Game Service
    participant Logic as Sudoku Logic
    participant Store as Game Store
    participant Scores as Leaderboard

    Player->>UI: Select difficulty
    UI->>API: GET /new?difficulty=medium
    API->>Service: create_game(medium)
    Service->>Logic: generate_unique_puzzle(medium)
    Logic-->>Service: puzzle, solution, clue metadata
    Service->>Store: save(gameId, game state)
    Store-->>Service: gameId
    Service-->>API: gameId and puzzle only
    API-->>UI: new game response
    UI->>UI: Render board and start timer

    Player->>UI: Enter a value
    UI->>UI: Detect row, column, or box conflicts
    UI-->>Player: Immediate accessible feedback

    Player->>UI: Click Hint
    UI->>API: POST /hint(gameId, board)
    API->>Service: request_hint(gameId, board)
    Service->>Logic: choose valid empty cell
    Logic-->>Service: one correct cell
    Service-->>API: row, column, value
    API-->>UI: hint response
    UI->>UI: Fill and lock hinted cell

    Player->>UI: Click Check
    UI->>API: POST /check(gameId, board)
    API->>Service: check_board(gameId, board)
    Service->>Logic: validate board
    Logic-->>Service: conflicts, incorrect cells, complete
    Service-->>API: safe validation result
    API-->>UI: check response
    UI-->>Player: Highlight incorrect entries

    alt Correct complete board
        UI->>UI: Stop timer
        UI-->>Player: Show congratulations
        Player->>UI: Enter name
        UI->>Scores: add score(name, time, difficulty, hints)
        Scores->>Scores: Sort and keep fastest ten
        Scores->>Scores: Save to localStorage
    end
```

## 3. Game state view

```mermaid
stateDiagram-v2
    [*] --> Loading
    Loading --> Playing: game created
    Loading --> Error: API failure
    Error --> Loading: retry or new game

    Playing --> Playing: valid entry
    Playing --> Conflict: duplicate row/column/box value
    Conflict --> Playing: value corrected or removed
    Playing --> HintRequested: Hint clicked
    HintRequested --> Playing: valid cell filled and locked
    HintRequested --> Error: hint unavailable
    Playing --> Checking: Check clicked
    Conflict --> Checking: Check clicked
    Checking --> Playing: incomplete or incorrect board
    Checking --> Completed: board is correct
    Completed --> ScoreEntry: name requested
    ScoreEntry --> LeaderboardUpdated: score saved
    LeaderboardUpdated --> [*]

    Playing --> Loading: New Game or difficulty changed
```

## 4. Domain and service view

```mermaid
classDiagram
    class GameSession {
        +game_id: str
        +difficulty: Difficulty
        +puzzle: Board
        +solution: Board
        +created_at: datetime
        +hints_used: int
    }

    class Difficulty {
        <<enumeration>>
        EASY
        MEDIUM
        HARD
    }

    class Board {
        +cells: int[9][9]
        +is_complete(): bool
    }

    class SudokuGenerator {
        +generate_solution(): Board
        +generate_unique_puzzle(difficulty): Board
        +count_solutions(board, limit=2): int
    }

    class SudokuValidator {
        +find_conflicts(board): Conflict[*]
        +find_incorrect(board, solution): Cell[*]
        +is_solved(board, solution): bool
    }

    class GameService {
        +create_game(difficulty): GameSession
        +request_hint(game_id, board): Cell
        +check_game(game_id, board): CheckResult
    }

    class GameStore {
        +save(game): void
        +get(game_id): GameSession
        +delete(game_id): void
    }

    GameSession --> Difficulty
    GameSession --> Board
    GameService --> SudokuGenerator
    GameService --> SudokuValidator
    GameService --> GameStore
    SudokuGenerator --> Board
    SudokuValidator --> Board
```

The solution may exist inside a server-side `GameSession`, but it must not be serialized into normal browser responses. The browser receives only the puzzle and safe validation or hint results.
