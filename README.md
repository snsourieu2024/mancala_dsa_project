# Mancala — DSA Project 

*  Correct rules (sowing, skipping opponent store, capture, extra turn, end-of-game collection)
*  Undo/Redo using **stacks**
*  AI via **Minimax + Alpha-Beta pruning**, **move ordering**, and a **transposition table** (Zobrist hashing)
*  Greedy hint (evaluation-only lookahead)
*  **GUI** using `game2dboard` with animations and toolbar
*  Unit tests with `pytest`

---

## How to run

> **Use your virtual environment.** In VS Code’s Git Bash:

```bash
source .venv/Scripts/activate
```

Install deps (first time or after pull):

```bash
pip install -r requirements.txt
```

Run the **GUI**:

```bash
python -m mancala.main --gui
```

Run the **CLI** (text mode):

```bash
python -m mancala.main
```

Run tests:

```bash
python -m pytest -q
```

---

## How to play (GUI)

When you start the GUI, you’ll see a **3×8 board**:

* **Top row**: Player **B**’s pits `[12..7]` and **B’s store** on the left
* **Middle row**: **Toolbar** (buttons and depth indicator)
* **Bottom row**: Player **A**’s pits `[0..5]` and **A’s store** on the right

You are **Player A** (bottom row). The computer is **Player B** (top row).

### Goal

Collect more stones in your **store** than your opponent by the end of the game.

### Your turn

* **Click** one of your pits (bottom row indices `0–5`) that has stones.
* Stones **sow** one by one counter-clockwise, **skipping the opponent’s store**.
* If your **last stone** lands in your **own store**, you get an **extra turn**.
* If your **last stone** lands in an **empty pit on your side**, and the **opposite pit** has stones, you **capture** both that last stone and the stones across into your store (the GUI sparkles the store briefly).

### End of game

When one side’s pits are empty, the remaining stones on the other side are collected into that side’s store. Highest store wins.

---

## GUI Controls

**Toolbar (middle row):**

* **[Undo]**: undo the last move
* **[Redo]**: redo an undone move
* **[Hint]**: shows a **greedy** suggested pit (quick heuristic)
* **[New]**: start a new game
* **[Depth-] / [Depth+]**: decrease/increase AI search depth (1–10)
* **Depth=**: shows current AI depth
* **Turn:** shows whose turn it is (A or B)

**Keyboard shortcuts:**

* `u` → Undo
* `r` → Redo
* `g` → Greedy hint

**Notes:**

* Legal pits on your side are subtly **highlighted** (via glow symbols) to indicate they’re clickable.
* The AI’s turn animates sowing as well—please give it a moment if the search depth is high.

---

## Project structure

```
mancala/
  rules.py      # constants, pit indices, helpers (stores, opposites)
  board.py      # Board state, move application, capture, end-of-game, legal moves
  history.py    # Undo/redo stacks
  tt.py         # Zobrist hashing for transposition table keys
  ai.py         # Minimax + alpha-beta + move ordering + TT; greedy hint; evaluation
  ui.py         # CLI + GUI (game2dboard) with animations & toolbar
  main.py       # argparse entrypoint for CLI/GUI
tests/
  test_board.py
  test_history.py
  test_ai.py
README.md
DESIGN.md
requirements.txt
```

---

## Syllabus mapping (what we demonstrate)

* **Arrays**: board representation (`board.py`)
* **Stacks & Queues**: undo/redo stacks (`history.py`)
* **Algorithm analysis**: discuss branching factor / depths in `DESIGN.md`
* **Recursion**: minimax search (`ai.py`)
* **Divide & Conquer**: game tree search decomposition
* **Sorting / Heaps**: move ordering uses sorting (could switch to heap easily)
* **Hash tables**: transposition table with Zobrist hashing (`tt.py`)
* **Graphs/Trees**: game tree exploration with alpha-beta pruning
* **Greedy**: hint function (one-step heuristic)
* **Dynamic Programming flavor**: TT caches overlapping positions to avoid recomputation

---

## Troubleshooting

* **GUI falls back to CLI**
  You’re not in the venv or `game2dboard` isn’t installed.

  ```bash
  source .venv/Scripts/activate
  python -c "import game2dboard, sys; print(game2dboard.__version__)"
  pip install game2dboard
  ```

* **Tkinter color error**
  We use **hex colors** (e.g., `"#d2d2d2"`). If you edited UI colors, keep hex strings.

* **Imports fail in tests**
  Make sure you’re at the project root and using:

  ```bash
  python -m pytest -q
  ```

  (We also include a `pytest.ini` with `pythonpath=.` if needed.)

* **AI too slow**
  Lower depth with **[Depth-]** or run:

  ```bash
  python -m mancala.main --gui --depth 4
  ```


