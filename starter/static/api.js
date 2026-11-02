/** Fetch JSON and turn the application's error envelope into an Error. */
async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload?.error?.message || "The request could not be completed.";
    throw new Error(message);
  }
  return payload;
}

export function createGame(difficulty) {
  return requestJson(`/new?difficulty=${encodeURIComponent(difficulty)}`);
}

export function requestHint(gameId, board) {
  return requestJson("/hint", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gameId, board }),
  });
}

export function checkBoard(gameId, board) {
  return requestJson("/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ gameId, board }),
  });
}
