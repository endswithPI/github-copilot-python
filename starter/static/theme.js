const THEME_KEY = "sudoku.theme";

function savedTheme() {
  try {
    const theme = localStorage.getItem(THEME_KEY);
    return theme === "light" || theme === "dark" ? theme : null;
  } catch {
    return null;
  }
}

function preferredTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function initializeTheme(toggle) {
  function apply(theme, persist = false) {
    document.documentElement.dataset.theme = theme;
    toggle.setAttribute("aria-pressed", String(theme === "dark"));
    if (persist) {
      try {
        localStorage.setItem(THEME_KEY, theme);
      } catch {
        // A browser can deny storage without preventing theme changes.
      }
    }
  }

  apply(savedTheme() || preferredTheme());
  toggle.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    apply(nextTheme, true);
  });
}
