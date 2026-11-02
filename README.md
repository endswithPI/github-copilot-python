# Sudoku Studio

A responsive Flask Sudoku game with unique-solution puzzles, immediate conflict feedback, hints, a timer, light and dark themes, and a browser-local Top 10 leaderboard.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Requirements

```
- Modern web browser (Chrome, Firefox, Edge, etc.)
- Python 3
```

### Installation

1. Fork this repository to your GitHub account. (You can use the "Fork" button on the top right corner of the repository page.)

2. Clone your forked repository to your local machine.

3. Open a terminal window and navigate to the "github-copilot-python/starter" directory.

4. Create a Python virtual environment and activate it.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

5. Install required Python packages.

```bash
pip install -r requirements.txt
```

6. Run the Flask app.

```bash
python app.py
```

7. Open http://127.0.0.1:5000 in your browser.

## Features

- Easy, Medium, and Hard puzzles with different clue-density targets.
- Puzzle generation that verifies exactly one solution remains.
- Locked original clues and locked hint cells.
- Immediate row, column, and 3×3-square conflict feedback.
- Server-validated Check and Hint actions.
- Automatic completion confirmation, timer, and score entry.
- Browser-local Top 10 scores with name, time, difficulty, and hints used.
- Persistent light or dark theme preference.
- Responsive board layout, keyboard focus indicators, and accessible status messages.

The Top 10 list and theme choice are stored in this browser's local storage. They are personal to the browser and are not a shared or secure leaderboard.

## Tests

From the `starter` directory, run:

```bash
python -m unittest discover -s tests -v
```

The suite verifies Sudoku uniqueness, difficulty clue targets, invalid boards, service behavior, and Flask API error contracts.

## Design guidance

Implementation rules and verification expectations are in [starter/instruction.md](starter/instruction.md). The target system diagrams are in [starter/docs/uml.md](starter/docs/uml.md).
