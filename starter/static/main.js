import { checkBoard, createGame, requestHint } from "./api.js";
import { createBoard, renderBoard } from "./board.js";
import {
  applyCheckResult,
  applyHint,
  createGameState,
  isBoardFull,
  updateCell,
} from "./game-state.js";
import { addScore, loadLeaderboard, renderLeaderboard } from "./leaderboard.js";
import { initializeTheme } from "./theme.js";
import { createTimer, formatTime } from "./timer.js";

const elements = {
  board: document.getElementById("sudoku-board"),
  difficulty: document.getElementById("difficulty"),
  timer: document.getElementById("timer"),
  newGame: document.getElementById("new-game"),
  hint: document.getElementById("hint-button"),
  check: document.getElementById("check-button"),
  message: document.getElementById("message"),
  completion: document.getElementById("completion-panel"),
  completionSummary: document.getElementById("completion-summary"),
  scoreForm: document.getElementById("score-form"),
  playerName: document.getElementById("player-name"),
  leaderboard: document.getElementById("leaderboard"),
  themeToggle: document.getElementById("theme-toggle"),
};

let state = null;
let loading = false;
const timer = createTimer(elements.timer);

function announce(message, isError = false) {
  elements.message.textContent = message;
  elements.message.classList.toggle("is-error", isError);
}

function setLoading(isLoading) {
  loading = isLoading;
  elements.newGame.disabled = isLoading;
  elements.difficulty.disabled = isLoading;
  elements.hint.disabled = isLoading || Boolean(state?.complete);
  elements.check.disabled = isLoading || Boolean(state?.complete);
}

function render() {
  if (state) {
    renderBoard(elements.board, state);
  }
}

async function startNewGame() {
  setLoading(true);
  elements.completion.hidden = true;
  elements.scoreForm.reset();
  elements.scoreForm.hidden = false;
  try {
    const payload = await createGame(elements.difficulty.value);
    state = createGameState(payload);
    timer.start();
    render();
    announce(`${payload.difficulty[0].toUpperCase()}${payload.difficulty.slice(1)} puzzle ready.`);
  } catch (error) {
    announce(error.message, true);
  } finally {
    setLoading(false);
  }
}

async function checkCurrentBoard(showSuccessMessage = true) {
  if (!state || loading) {
    return false;
  }
  setLoading(true);
  try {
    const result = await checkBoard(state.gameId, state.board);
    const complete = applyCheckResult(state, result);
    render();
    if (complete) {
      completeGame();
      return true;
    }
    if (result.incorrect.length) {
      announce(`${result.incorrect.length} entr${result.incorrect.length === 1 ? "y is" : "ies are"} incorrect.`, true);
    } else if (result.conflicts.length) {
      announce("Resolve the highlighted conflicts before continuing.", true);
    } else if (showSuccessMessage) {
      announce("No incorrect entries so far. Keep going!");
    }
  } catch (error) {
    announce(error.message, true);
  } finally {
    setLoading(false);
  }
  return false;
}

function completeGame() {
  if (state.complete) {
    return;
  }
  state.complete = true;
  timer.stop();
  render();
  const elapsed = timer.elapsedSeconds();
  elements.completionSummary.textContent = `You solved this ${state.difficulty} puzzle in ${formatTime(elapsed)} using ${state.hintsUsed} hint${state.hintsUsed === 1 ? "" : "s"}.`;
  elements.completion.hidden = false;
  elements.playerName.focus();
  announce("Congratulations, puzzle solved!");
}

async function giveHint() {
  if (!state || loading || state.complete) {
    return;
  }
  let shouldCheckCompletion = false;
  setLoading(true);
  try {
    const hint = await requestHint(state.gameId, state.board);
    applyHint(state, hint);
    render();
    announce("A correct cell has been filled and locked.");
    shouldCheckCompletion = isBoardFull(state.board);
  } catch (error) {
    announce(error.message, true);
  } finally {
    setLoading(false);
  }
  if (shouldCheckCompletion) {
    await checkCurrentBoard(false);
  }
}

async function onCellInput(row, col, value) {
  if (!state || loading) {
    return;
  }
  updateCell(state, row, col, value);
  render();
  if (state.conflicts.size) {
    announce("A highlighted value conflicts with its row, column, or square.", true);
    return;
  }
  if (isBoardFull(state.board)) {
    await checkCurrentBoard(false);
  }
}

function saveScore(event) {
  event.preventDefault();
  if (!state || !state.complete || state.scoreSaved) {
    return;
  }
  const name = elements.playerName.value.trim().slice(0, 24) || "Player";
  const scores = addScore({
    name,
    timeSeconds: timer.elapsedSeconds(),
    difficulty: state.difficulty,
    hintsUsed: state.hintsUsed,
    createdAt: new Date().toISOString(),
  });
  state.scoreSaved = true;
  renderLeaderboard(elements.leaderboard, scores);
  elements.scoreForm.hidden = true;
  announce("Your score has been saved in this browser.");
}

function initialise() {
  initializeTheme(elements.themeToggle);
  createBoard(elements.board, onCellInput);
  renderLeaderboard(elements.leaderboard, loadLeaderboard());
  elements.newGame.addEventListener("click", startNewGame);
  elements.hint.addEventListener("click", giveHint);
  elements.check.addEventListener("click", () => checkCurrentBoard());
  elements.difficulty.addEventListener("change", startNewGame);
  elements.scoreForm.addEventListener("submit", saveScore);
  startNewGame();
}

initialise();
