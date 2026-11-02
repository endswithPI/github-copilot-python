const SIZE = 9;

export function cellKey(row, col) {
  return `${row}-${col}`;
}

function copyBoard(board) {
  return board.map((row) => [...row]);
}

export function createGameState(payload) {
  const lockedCells = new Set();
  payload.puzzle.forEach((row, rowIndex) => {
    row.forEach((value, colIndex) => {
      if (value !== 0) {
        lockedCells.add(cellKey(rowIndex, colIndex));
      }
    });
  });

  return {
    gameId: payload.gameId,
    difficulty: payload.difficulty,
    board: copyBoard(payload.puzzle),
    lockedCells,
    hintedCells: new Set(),
    conflicts: new Set(),
    incorrectCells: new Set(),
    hintsUsed: 0,
    complete: false,
    scoreSaved: false,
  };
}

export function findConflicts(board) {
  const conflicts = new Set();

  function markDuplicates(cells) {
    const values = new Map();
    cells.forEach(([row, col]) => {
      const value = board[row][col];
      if (value !== 0) {
        const entries = values.get(value) || [];
        entries.push(cellKey(row, col));
        values.set(value, entries);
      }
    });
    values.forEach((entries) => {
      if (entries.length > 1) {
        entries.forEach((key) => conflicts.add(key));
      }
    });
  }

  for (let index = 0; index < SIZE; index += 1) {
    markDuplicates(Array.from({ length: SIZE }, (_, col) => [index, col]));
    markDuplicates(Array.from({ length: SIZE }, (_, row) => [row, index]));
  }
  for (let startRow = 0; startRow < SIZE; startRow += 3) {
    for (let startCol = 0; startCol < SIZE; startCol += 3) {
      markDuplicates(
        Array.from({ length: 9 }, (_, index) => [
          startRow + Math.floor(index / 3),
          startCol + (index % 3),
        ]),
      );
    }
  }
  return conflicts;
}

export function updateCell(state, row, col, value) {
  const key = cellKey(row, col);
  if (state.lockedCells.has(key) || state.complete) {
    return;
  }
  state.board[row][col] = value;
  state.incorrectCells.delete(key);
  state.conflicts = findConflicts(state.board);
}

export function applyHint(state, hint) {
  const key = cellKey(hint.row, hint.col);
  state.board[hint.row][hint.col] = hint.value;
  state.lockedCells.add(key);
  state.hintedCells.add(key);
  state.hintsUsed += 1;
  state.incorrectCells.delete(key);
  state.conflicts = findConflicts(state.board);
}

export function applyCheckResult(state, result) {
  state.conflicts = new Set(result.conflicts.map(([row, col]) => cellKey(row, col)));
  state.incorrectCells = new Set(result.incorrect.map(([row, col]) => cellKey(row, col)));
  return result.complete;
}

export function isBoardFull(board) {
  return board.every((row) => row.every((value) => value !== 0));
}
