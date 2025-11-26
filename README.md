# Mancala — DSA Project

A full-featured Mancala implementation demonstrating multiple Data Structures and Algorithms concepts:

* Correct rules (sowing, skipping opponent store, capture, extra turn, end-of-game collection)
* Undo/Redo using **stacks**
* AI via **Minimax + Alpha-Beta pruning**, **move ordering**, and a **transposition table** (Zobrist hashing)
* Greedy hint (evaluation-only lookahead)
* **GUI** using `game2dboard` with animations and toolbar
* Local **Multiplayer GUI** (Tkinter)
* Central **Launcher** (`play.py`) to choose Singleplayer or Multiplayer modes
* Unit tests with `pytest`

---

## Project Structure

```
mancala_dsa_project/
│
├── Multiplayer/
│ ├── game.py
│ └── UI.py
│
├── Singleplayer/
│ ├── mancala/
│ │ ├── init.py
│ │ ├── ai.py
│ │ ├── board.py
│ │ ├── history.py
│ │ ├── main.py
│ │ ├── rules.py
│ │ ├── tt.py
│ │ └── ui.py
│ │
│ ├── tests/
│ │ ├──test_ai.py
│ │ ├──test_board.py
│ │ └──test_history.py
│ │
│ └── pytest.ini
│
├── play.py
├── README.md
└── requirements.txt
```

---

## Installation

### 1. Activate virtual environment  
(Example for VS Code using Git Bash)

```bash
source .venv/Scripts/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run the Game

### ▶ **Recommended: Use the Unified Launcher**

From the **project root**:

```bash
python play.py
```

This opens a Tkinter launcher with:

- **Singleplayer** (AI vs Human, game2dboard GUI)
- **Multiplayer** (local 2-player Tkinter GUI)
- **Rules**
- **Mode previews**

---

## Running Modes Directly (Optional)

### ▶ **Singleplayer GUI**

```bash
cd Singleplayer/
python -m mancala.main --gui
```

### ▶ **Singleplayer CLI**

```bash
cd Singleplayer/
python -m mancala.main
```

### ▶ **Multiplayer GUI**

```bash
python Multiplayer/UI.py
```

---
## Mancala Rules Summary

- Pick a pit on your side.
- Sow stones counter-clockwise.
- Skip the opponent's store.
- Extra turn if your last stone lands in your store.
- Capture if your last stone lands in an empty pit on your side and opposite pit has stones.
- Game ends when one side is empty; remaining stones collected.


## How to Play (Singleplayer GUI)

When the Singleplayer GUI starts, you’ll see a **3×8 board**:

- **Top row**: Player **B**’s pits `[12..7]` and **B’s store** (left)
- **Middle**: Toolbar (Undo/Redo/Hint/New/Depth controls)
- **Bottom row**: Player **A**’s pits `[0..5]` and **A’s store** (right)

You are **Player A** (bottom row). The AI is **Player B** (top row).

### GUI Toolbar

- **Undo / Redo**  
- **Hint** (greedy evaluation)
- **New game**
- **AI Depth- / Depth+** (1–10)
- **Depth = X** indicator
- **Turn:** A or B  
- **Keyboard shortcuts**:
  - `u` → Undo
  - `r` → Redo
  - `g` → Hint

---

## Multiplayer GUI (Tkinter)

- Local 2-player mode
- Styled board
- Clear player sides
- Rules button
- **Main Menu** button to return to `play.py`
- Game messages displayed below the board

---

## Running Tests

From the project root:

```bash
cd Singleplayer/
python -m pytest -q
```

---

## Syllabus Mapping (DSA Topics Demonstrated)

| Topic | Where Used |
|-------|------------|
| **Arrays** | Board representation (`board.py`) |
| **Stacks** | Undo/Redo (`history.py`) |
| **Queues** | Implicit in sowing & AI exploration |
| **Recursion** | Minimax search (`ai.py`) |
| **Divide & Conquer** | Game tree splitting |
| **Sorting / Move Ordering** | Sorting moves heuristically in AI |
| **Hash Tables** | Transposition table with Zobrist hashing (`tt.py`) |
| **Graphs / Trees** | Game tree exploration |
| **Greedy Algorithms** | Hint move |
| **Dynamic Programming flavor** | TT caching of repeated states |
| **Algorithm Analysis** | Search depth & branching factor in `DESIGN.md` |

---

## Troubleshooting

### GUI falls back to CLI
You’re not in the virtual environment or `game2dboard` is missing:

```bash
source .venv/Scripts/activate
pip install game2dboard
```

### Tkinter color errors  
Use proper **hex color strings** (`"#123abc"`).

### Tests fail due to import errors
Run tests from the project root:

```bash
python -m pytest -q
```

### AI is slow
Lower depth:

```bash
python -m mancala.main --gui --depth 4
```

---

Enjoy Mancala! 🎉
