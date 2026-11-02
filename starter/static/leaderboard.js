const LEADERBOARD_KEY = "sudoku.leaderboard.v1";

function storageAvailable() {
  try {
    const probe = "__sudoku_storage_probe__";
    localStorage.setItem(probe, "1");
    localStorage.removeItem(probe);
    return true;
  } catch {
    return false;
  }
}

export function loadLeaderboard() {
  if (!storageAvailable()) {
    return [];
  }
  try {
    const parsed = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || "[]");
    return Array.isArray(parsed) ? parsed.filter(isScore) : [];
  } catch {
    return [];
  }
}

function isScore(score) {
  return score
    && typeof score.name === "string"
    && Number.isInteger(score.timeSeconds)
    && typeof score.difficulty === "string"
    && Number.isInteger(score.hintsUsed);
}

export function addScore(score) {
  const scores = [...loadLeaderboard(), score]
    .sort((left, right) => left.timeSeconds - right.timeSeconds || left.hintsUsed - right.hintsUsed)
    .slice(0, 10);
  if (storageAvailable()) {
    try {
      localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
    } catch {
      // The completed game remains playable if storage is full or unavailable.
    }
  }
  return scores;
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${String(seconds % 60).padStart(2, "0")}`;
}

export function renderLeaderboard(element, scores) {
  element.replaceChildren();
  if (!scores.length) {
    const item = document.createElement("li");
    item.className = "empty-score";
    item.textContent = "Complete a puzzle to record your first score.";
    element.append(item);
    return;
  }

  scores.forEach((score) => {
    const item = document.createElement("li");
    const name = document.createElement("strong");
    name.textContent = score.name;
    const details = document.createElement("span");
    details.textContent = `${formatTime(score.timeSeconds)} · ${score.difficulty} · ${score.hintsUsed} hint${score.hintsUsed === 1 ? "" : "s"}`;
    item.append(name, details);
    element.append(item);
  });
}
