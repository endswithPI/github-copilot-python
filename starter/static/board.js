import { cellKey } from "./game-state.js";

const SIZE = 9;

function boxTone(row, col) {
  return (Math.floor(row / 3) + Math.floor(col / 3)) % 2 === 0 ? "box-even" : "box-odd";
}

function cellLabel(row, col) {
  return `Row ${row + 1}, column ${col + 1}`;
}

function normalizeValue(value) {
  const digits = value.replace(/[^1-9]/g, "");
  return digits ? Number(digits.at(-1)) : 0;
}

export function createBoard(element, onInput) {
  const fragment = document.createDocumentFragment();
  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      const input = document.createElement("input");
      input.className = `sudoku-cell ${boxTone(row, col)}`;
      input.id = `cell-${row}-${col}`;
      input.type = "text";
      input.inputMode = "numeric";
      input.maxLength = 1;
      input.autocomplete = "off";
      input.dataset.row = String(row);
      input.dataset.col = String(col);
      input.setAttribute("role", "gridcell");
      input.setAttribute("aria-label", cellLabel(row, col));
      fragment.append(input);
    }
  }
  element.replaceChildren(fragment);

  element.addEventListener("input", (event) => {
    const input = event.target;
    if (!(input instanceof HTMLInputElement) || !input.classList.contains("sudoku-cell")) {
      return;
    }
    const value = normalizeValue(input.value);
    input.value = value || "";
    onInput(Number(input.dataset.row), Number(input.dataset.col), value);
  });
}

export function renderBoard(element, state) {
  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      const key = cellKey(row, col);
      const input = element.querySelector(`#cell-${row}-${col}`);
      const locked = state.lockedCells.has(key);
      const hinted = state.hintedCells.has(key);
      const conflict = state.conflicts.has(key);
      const incorrect = state.incorrectCells.has(key);

      input.value = state.board[row][col] || "";
      input.disabled = locked || state.complete;
      input.classList.toggle("is-clue", locked && !hinted);
      input.classList.toggle("is-hint", hinted);
      input.classList.toggle("is-conflict", conflict);
      input.classList.toggle("is-incorrect", incorrect);
      input.setAttribute("aria-invalid", String(conflict || incorrect));
      input.setAttribute("aria-label", `${cellLabel(row, col)}${locked ? hinted ? ", hint" : ", clue" : ""}${conflict ? ", conflicts with another cell" : ""}${incorrect ? ", incorrect" : ""}`);
    }
  }
}
