function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
  const seconds = (totalSeconds % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
}

export function createTimer(element) {
  let startedAt = null;
  let elapsedBeforeStart = 0;
  let intervalId = null;

  function elapsedSeconds() {
    if (startedAt === null) {
      return elapsedBeforeStart;
    }
    return elapsedBeforeStart + Math.floor((Date.now() - startedAt) / 1000);
  }

  function render() {
    element.textContent = formatTime(elapsedSeconds());
  }

  return {
    start() {
      this.stop();
      elapsedBeforeStart = 0;
      startedAt = Date.now();
      render();
      intervalId = window.setInterval(render, 250);
    },
    stop() {
      if (startedAt !== null) {
        elapsedBeforeStart = elapsedSeconds();
        startedAt = null;
      }
      if (intervalId !== null) {
        window.clearInterval(intervalId);
        intervalId = null;
      }
      render();
    },
    elapsedSeconds,
  };
}

export { formatTime };
