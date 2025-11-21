from .board import Board
from .history import History
from .ai import AI
from .rules import PLAYER_A, PLAYER_B, A_STORE, B_STORE

def run_cli(start_stones: int = 4, depth: int = 6):
    b = Board.new(start_stones)
    hist = History()
    ai = AI(depth=depth)

    def draw():
        pits = b.pits
        print("\n" + "="*38)
        print("          [12][11][10][09][08][07]")
        print("      B  ", " ".join(f"{pits[i]:2d}" for i in range(12,6,-1)))
        print(f"[{pits[B_STORE]:2d}]                          [{pits[A_STORE]:2d}]")
        print("      A  ", " ".join(f"{pits[i]:2d}" for i in range(0,6)))
        print("          [00][01][02][03][04][05]")
        print(f"Turn: {'A' if b.current==PLAYER_A else 'B'}")

    draw()
    while True:
        if b.terminal():
            a, c = b.score(PLAYER_A), b.score(PLAYER_B)
            print(f"Game over. A={a} B={c}. Winner: {'A' if a>c else 'B' if c>a else 'Draw'}")
            break
        if b.current == PLAYER_B:
            res = ai.choose(b)
            mv = res.move
            print(f"AI chooses {mv} | nodes: {res.nodes}")
        else:
            legal = b.legal_moves()
            s = input(f"Choose pit from {legal} (u=undo,r=redo,g=hint,q=quit): ").strip().lower()
            if s == 'q': break
            if s == 'u':
                if hist.undo(b): draw()
                else: print("Nothing to undo.")
                continue
            if s == 'r':
                if hist.redo(b): draw()
                else: print("Nothing to redo.")
                continue
            if s == 'g':
                hint = ai.greedy_hint(b)
                print("Greedy hint:", hint)
                continue
            try:
                mv = int(s)
            except ValueError:
                print("Enter a number or command."); continue
            if mv not in legal:
                print("Illegal move."); continue
        hist.push(b)
        b.apply_move(mv)
        draw()

def run_gui(start_stones: int = 4, depth: int = 6):
    try:
        from game2dboard import Board as GBoard
    except Exception:
        print("game2dboard not installed; falling back to CLI.")
        return run_cli(start_stones, depth)

    import time
    from .board import Board
    from .history import History
    from .ai import AI
    from .rules import PLAYER_A, PLAYER_B, A_STORE, B_STORE, pit_range

    # --- model ---
    b = Board.new(start_stones)
    hist = History()
    ai = AI(depth=depth)

    # --- layout: 3 rows x 8 cols ---
    # row 0: B side (left store + 12..7)
    # row 1: toolbar buttons
    # row 2: A side (0..5 + right store)
    rows, cols = 3, 8
    gb = GBoard(rows, cols)
    gb.title = "Mancala – DSA Edition"
    gb.cell_size = 90
    gb.grid_color = "#d2d2d2"   # light gray
    gb.font_color = "#141414"   # near-black


    # --- theme helpers ---
    STONE = "●"
    GLOW = "◉"
    SPARKLE = "✨"

    def pit_label(count: int, glow: bool = False, idx: int | None = None) -> str:
        # render up to 10 stones as circles, then show "+n"
        if count <= 10:
            dots = (STONE if not glow else GLOW) * count
            line = dots if dots else ("·" if not glow else "˚")
        else:
            dots = (STONE if not glow else GLOW) * 10
            line = f"{dots}+{count-10}"
        if idx is not None:
            return f"{line}\n[{idx:02d}]"
        return line

    def store_label(count: int, owner: str, sparkle: bool = False) -> str:
        jar = "│" + (" " * 5) + "│"
        cap = "┌─────┐"
        base = "└─────┘"
        stars = SPARKLE if sparkle else ""
        return f"{cap}\n{jar}\n{jar}\n{base}\n{owner} {count:02d} {stars}"

    # --- toolbar mapping ---
    # Clickable "buttons" in row 1
    TOOL_CELLS = {
        (1, 1): "Undo",
        (1, 2): "Redo",
        (1, 3): "Hint",
        (1, 4): "New",
        (1, 5): "Depth-",
        (1, 6): "Depth+",
    }

    def toolbar_cell_text(r, c):
        label = TOOL_CELLS.get((r, c), "")
        return f"[{label}]" if label else ""

    # --- render ---
    def legal_glow_indices():
        return set(i for i in pit_range(b.current) if b.pits[i] > 0)

    def refresh(sparkle_store: int | None = None):
        gb.clear()
        glow = legal_glow_indices()

        # Row 0: B store + 12..7
        gb[0][0] = store_label(b.pits[B_STORE], "Store B",
                               sparkle=(sparkle_store == B_STORE))
        for j, idx in enumerate(range(12, 7-1, -1), start=1):
            gb[0][j] = pit_label(b.pits[idx], glow=(idx in glow), idx=idx)

        # Row 1: toolbar
        for c in range(cols):
            gb[1][c] = toolbar_cell_text(1, c)
        gb[1][0] = f"Depth={ai.depth}"
        gb[1][7] = "Turn: " + ("A" if b.current == PLAYER_A else "B")

        # Row 2: 0..5 + A store
        for j, idx in enumerate(range(0, 6), start=0):
            gb[2][j] = pit_label(b.pits[idx], glow=(idx in glow), idx=idx)
        gb[2][7] = store_label(b.pits[A_STORE], "Store A",
                               sparkle=(sparkle_store == A_STORE))

        gb.caption = f"A={b.pits[A_STORE]}  |  B={b.pits[B_STORE]}"

    # --- animation: sow seeds pit-by-pit with small delays ---
    def animate_sow(start_idx: int) -> tuple[bool, str | None, int | None]:
        """
        Returns (extra_turn, end_reason, captured_store_idx)
        captured_store_idx is A_STORE or B_STORE when a capture occurred; otherwise None.
        """
        player = b.current
        stones = b.pits[start_idx]
        b.pits[start_idx] = 0
        idx = start_idx
        captured_store_idx = None

        while stones > 0:
            idx = (idx + 1) % 14
            # skip opponent store
            if idx == (A_STORE if player == PLAYER_B else B_STORE):
                continue
            b.pits[idx] += 1
            refresh()
            gb.update()
            time.sleep(0.11)
            stones -= 1

        extra_turn = (idx == (A_STORE if player == PLAYER_A else B_STORE))

        # capture check (mirrors Board.apply_move but animated) — works for both players
        if (not extra_turn) and (idx in pit_range(player)) and b.pits[idx] == 1:
            opp_idx = 12 - idx               # opposite pit for both sides
            cap = b.pits[opp_idx]
            if cap > 0:
                opp_store = (B_STORE if player == PLAYER_A else A_STORE)
                b.pits[opp_store] += cap + 1
                b.pits[idx] = 0
                b.pits[opp_idx] = 0
                captured_store_idx = opp_store
                refresh(sparkle_store=opp_store)
                gb.update()
                time.sleep(0.22)

        # end condition (collection)
        from .rules import PLAYER_A, PLAYER_B, pit_range, A_STORE, B_STORE
        end_reason = None
        if all(b.pits[i] == 0 for i in pit_range(PLAYER_A)) or \
           all(b.pits[i] == 0 for i in pit_range(PLAYER_B)):
            for i in pit_range(PLAYER_A):
                b.pits[A_STORE] += b.pits[i]; b.pits[i] = 0
            for i in pit_range(PLAYER_B):
                b.pits[B_STORE] += b.pits[i]; b.pits[i] = 0
            end_reason = "side_empty"
            refresh()
            gb.update()

        if not extra_turn and end_reason is None:
            b.current = PLAYER_B if player == PLAYER_A else PLAYER_A

        return extra_turn, end_reason, captured_store_idx

    # --- click mapping: pits for current player + toolbar buttons ---
    def handle_pit_click(row, col):
        # map GUI cell -> pit index
        if row == 2 and 0 <= col <= 5 and b.current == PLAYER_A:
            return col  # 0..5
        if row == 0 and 1 <= col <= 6 and b.current == PLAYER_B:
            return 13 - col  # 12..7
        return None

    def do_toolbar(row, col):
        nonlocal b, hist
        action = TOOL_CELLS.get((row, col))
        if not action:
            return False
        if action == "Undo":
            if hist.undo(b): refresh(); gb.update()
        elif action == "Redo":
            if hist.redo(b): refresh(); gb.update()
        elif action == "Hint":
            hint = ai.greedy_hint(b)
            gb.caption = gb.caption + f" | Hint: {hint}"
            gb.update()
        elif action == "New":
            b = Board.new(start_stones); hist = History()
            refresh(); gb.update()
        elif action == "Depth+":
            ai.depth = min(ai.depth + 1, 10)
            refresh(); gb.update()
        elif action == "Depth-":
            ai.depth = max(ai.depth - 1, 1)
            refresh(); gb.update()
        return True

    def human_play(pit):
        hist.push(b)
        # animate sow (also handles capture/extra/collection)
        animate_sow(pit)
        refresh(); gb.update()
        # AI autoplay (B)
        while not b.terminal() and b.current == PLAYER_B:
            mv = ai.choose(b).move
            if mv is None:
                break
            hist.push(b)
            # animate the AI move too
            animate_sow(mv)
            refresh(); gb.update()

    def onclick(row, col):
        # Buttons first
        if do_toolbar(row, col):
            return
        # Then pits
        pit = handle_pit_click(row, col)
        if pit is None:
            return
        if b.pits[pit] == 0:
            return
        human_play(pit)

    def onkey(k):
        if k == 'u':
            if hist.undo(b):
                refresh(); gb.update()
        elif k == 'r':
            if hist.redo(b):
                refresh(); gb.update()
        elif k == 'g':
            hint = ai.greedy_hint(b)
            gb.caption = gb.caption + f" | Hint: {hint}"
            gb.update()

    gb.onclick = onclick
    gb.onkey = onkey
    refresh()
    gb.show()
