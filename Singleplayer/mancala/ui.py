import os
import sys
import subprocess

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
        print("\n" + "=" * 38)
        print("          [12][11][10][09][08][07]")
        print("      B  ", " ".join(f"{pits[i]:2d}" for i in range(12, 6, -1)))
        print(f"[{pits[B_STORE]:2d}]                          [{pits[A_STORE]:2d}]")
        print("      A  ", " ".join(f"{pits[i]:2d}" for i in range(0, 6)))
        print("          [00][01][02][03][04][05]")
        print(f"Turn: {'A' if b.current == PLAYER_A else 'B'}")

    draw()
    while True:
        if b.terminal():
            a, c = b.score(PLAYER_A), b.score(PLAYER_B)
            print(
                f"Game over. A={a} B={c}. Winner: "
                f"{'A' if a > c else 'B' if c > a else 'Draw'}"
            )
            break
        if b.current == PLAYER_B:
            res = ai.choose(b)
            mv = res.move
            print(f"AI chooses {mv} | nodes: {res.nodes}")
        else:
            legal = b.legal_moves()
            s = input(
                f"Choose pit from {legal} (u=undo,r=redo,g=hint,q=quit): "
            ).strip().lower()
            if s == "q":
                break
            if s == "u":
                if hist.undo(b):
                    draw()
                else:
                    print("Nothing to undo.")
                continue
            if s == "r":
                if hist.redo(b):
                    draw()
                else:
                    print("Nothing to redo.")
                continue
            if s == "g":
                hint = ai.greedy_hint(b)
                print("Greedy hint:", hint)
                continue
            try:
                mv = int(s)
            except ValueError:
                print("Enter a number or command.")
                continue
            if mv not in legal:
                print("Illegal move.")
                continue
        hist.push(b)
        b.apply_move(mv)
        draw()



def run_gui(start_stones: int = 4, depth: int = 6):
    """
    You are Player A (bottom row).
    The AI is Player B (top row).
    """

    import tkinter as tk
    from tkinter import messagebox
    import os
    import sys
    import subprocess

    from .rules import PLAYER_A, PLAYER_B, A_STORE, B_STORE
    from .board import Board
    from .history import History
    from .ai import AI

    # --- model ---
    b = Board.new(start_stones)
    hist = History()
    ai = AI(depth=depth)
    game_over = False

    # --- shared colors (match multiplayer) ---
    bg_color = "#151726"
    board_bg = "#262b3f"
    store_bg_ai = "#4f9cff"     # AI store (top / left)
    store_bg_you = "#ffb347"    # Your store (bottom / right)

    # --- update pit colors in BOTH modes ---
    pit_bg_ai  = "#6c5ce7"  
    pit_bg_you = "#00cec9"  

    pit_fg = "#ffffff"
    text_color = "#f0f0f0"
    turn_highlight_color = "#ff0000"
    turn_inactive_color = "#888888"

    # --- UI state containers ---
    top_pit_buttons = []
    bottom_pit_buttons = []
    store_ai_label = None
    store_you_label = None
    depth_label = None
    status_label = None
    log_text = None
    p_ai_label = None
    p_you_label = None

    # --- pit indices ---
    top_indices = [12, 11, 10, 9, 8, 7]   # AI pits (B) left→right
    bottom_indices = [0, 1, 2, 3, 4, 5]   # Your pits (A) left→right

    # --- UI functions ---

    def go_to_main_menu():
        """Close this window and launch play.py """
        nonlocal root
        # ui.py -> mancala -> Singleplayer -> project root (mancala_dsa_project)
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        play_path = os.path.join(base_dir, "play.py")

        # optional safety check
        if not os.path.exists(play_path):
            from tkinter import messagebox
            messagebox.showerror(
                "Error",
                f"Could not find play.py at:\n{play_path}",
            )
            return

        root.destroy()
        subprocess.Popen([sys.executable, play_path], cwd=base_dir)


    def log(msg: str):
        nonlocal log_text
        if not msg:
            return
        log_text.config(state="normal")
        log_text.insert("end", msg + "\n")
        log_text.see("end")
        log_text.config(state="disabled")

    def refresh_board():
        """Update pits, stores, and whose turn highlight."""
        nonlocal top_pit_buttons, bottom_pit_buttons
        nonlocal store_ai_label, store_you_label
        nonlocal p_ai_label, p_you_label, depth_label, status_label

        # top row: AI pits 
        for col, idx in enumerate(top_indices):
            val = b.pits[idx]
            btn = top_pit_buttons[col]
            btn.config(text=str(val))
            btn.config(state="disabled")  # AI side is never clickable

        # bottom row: player pits
        for col, idx in enumerate(bottom_indices):
            val = b.pits[idx]
            btn = bottom_pit_buttons[col]
            btn.config(text=str(val))
            if (not game_over) and b.current == PLAYER_A and val > 0:
                btn.config(state="normal", relief="raised", bd=4)
            else:
                btn.config(state="disabled", relief="sunken", bd=2)

        # stores
        store_ai_label.config(text=str(b.pits[B_STORE]))
        store_you_label.config(text=str(b.pits[A_STORE]))

        # turn highlighting
        if not game_over and b.current == PLAYER_A:
            p_you_label.config(fg=turn_highlight_color)
            p_ai_label.config(fg=turn_inactive_color)
        elif not game_over and b.current == PLAYER_B:
            p_ai_label.config(fg=turn_highlight_color)
            p_you_label.config(fg=turn_inactive_color)
        else:
            p_ai_label.config(fg=turn_inactive_color)
            p_you_label.config(fg=turn_inactive_color)

        # other status
        depth_label.config(text=f"Depth: {ai.depth}")
        if game_over:
            a_score = b.score(PLAYER_A)
            b_score = b.score(PLAYER_B)
            if a_score > b_score:
                status_label.config(text=f"Game over: You win!  A={a_score}  B={b_score}")
            elif b_score > a_score:
                status_label.config(text=f"Game over: AI wins.  A={a_score}  B={b_score}")
            else:
                status_label.config(text=f"Game over: Draw.  A={a_score}  B={b_score}")
        else:
            status_label.config(
                text="Your turn." if b.current == PLAYER_A else "AI's turn..."
            )

    def finish_game():
        """Mark game as over, log winner, and show a dialog."""
        nonlocal game_over
        if game_over:
            return
        game_over = True
        a_score = b.score(PLAYER_A)
        b_score = b.score(PLAYER_B)
        if a_score > b_score:
            msg = f"Game over. You win! (A={a_score}, B={b_score})"
        elif b_score > a_score:
            msg = f"Game over. AI wins. (A={a_score}, B={b_score})"
        else:
            msg = f"Game over. It's a draw. (A={a_score}, B={b_score})"
        log(msg)
        refresh_board()
        messagebox.showinfo("Mancala", msg)

    def maybe_end_after_move() -> bool:
        """Check if game is terminal and finalize if so."""
        if b.terminal():
            finish_game()
            return True
        return False

    def new_game():
        """Reset board, history, and game_over flag."""
        nonlocal b, hist, game_over
        b = Board.new(start_stones)
        hist = History()
        game_over = False
        log("New singleplayer game started.")
        refresh_board()

    def human_move(pit_index: int):
        """Apply a human move, then let the AI respond."""
        nonlocal game_over

        if game_over:
            return
        if b.current != PLAYER_A:
            log("It's not your turn.")
            return

        legal = b.legal_moves()
        if pit_index not in legal:
            log(f"Illegal move: pit {pit_index}. Legal pits: {sorted(legal)}")
            return

        # apply human move
        hist.push(b)
        log(f"You play pit {pit_index}.")
        b.apply_move(pit_index)
        refresh_board()
        if maybe_end_after_move():
            return

        # Now let the AI play (after a short delay)
        def ai_turn():
            nonlocal game_over

            if game_over or b.terminal() or b.current != PLAYER_B:
                refresh_board()
                return

            status_label.config(text="AI is thinking...")
            root.update_idletasks()

            try:
                res = ai.choose(b)
            except Exception as e:
                log(f"AI error: {e!r}")
                refresh_board()
                return

            mv = res.move
            if mv is None:
                log("AI has no legal moves.")
                refresh_board()
                if maybe_end_after_move():
                    return
                return

            hist.push(b)
            log(f"AI plays pit {mv} (nodes searched: {res.nodes}).")
            b.apply_move(mv)
            refresh_board()

            if maybe_end_after_move():
                return

            # If AI gets another turn, schedule again
            if b.current == PLAYER_B and not b.terminal():
                root.after(300, ai_turn)

        # start AI after a short delay so user can see their move
        root.after(250, ai_turn)

    def do_undo():
        nonlocal game_over
        if hist.undo(b):
            log("Undo.")
            game_over = False
            refresh_board()
        else:
            log("Nothing to undo.")

    def do_redo():
        nonlocal game_over
        if hist.redo(b):
            log("Redo.")
            game_over = False
            refresh_board()
            if b.terminal():
                finish_game()
        else:
            log("Nothing to redo.")

    def do_hint():
        try:
            hint = ai.greedy_hint(b)
        except Exception as e:
            log(f"Hint error: {e!r}")
            return
        if hint is None:
            log("No hint available (no legal moves?).")
        else:
            log(f"Hint: consider playing pit {hint}.")

    def do_depth(delta: int):
        ai.depth = min(10, max(1, ai.depth + delta))
        log(f"AI depth set to {ai.depth}.")
        refresh_board()

    def show_rules():
        rules_win = tk.Toplevel(root)
        rules_win.title("Mancala – Rules")
        rules_win.configure(bg=bg_color)
        rules_win.geometry("520x520")
        rules_win.resizable(False, False)

        outer = tk.Frame(
            rules_win,
            bg=board_bg,
            bd=4,
            relief="ridge",
            padx=15,
            pady=15,
        )
        outer.pack(expand=True, fill="both", padx=20, pady=20)

        title = tk.Label(
            outer,
            text="Mancala Rules",
            font=("Helvetica", 20, "bold"),
            fg=text_color,
            bg=board_bg,
        )
        title.pack(pady=(0, 15))

        text_frame = tk.Frame(outer, bg=board_bg)
        text_frame.pack(expand=True, fill="both")

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        rules_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Helvetica", 12),
            bg=board_bg,
            fg=text_color,
            relief="flat",
            yscrollcommand=scrollbar.set,
        )
        rules_text.pack(expand=True, fill="both")
        scrollbar.config(command=rules_text.yview)

        rules_text.insert(
            "end",
            (
                "Basic Mancala Rules:\n\n"
                "- Each player owns the six pits on their side of the board.\n"
                "- You are the BOTTOM row. The AI is the TOP row.\n"
                "- Players take turns selecting one of their pits (not the store).\n\n"
                "Sowing Stones:\n"
                "- Pick up all stones from the chosen pit.\n"
                "- Moving counter-clockwise, drop one stone into each pit you pass.\n"
                "- Drop stones into your OWN store.\n"
                "- Skip your opponent's store.\n\n"
                "Extra Turn:\n"
                "- If your last stone lands in your own store, you get another turn.\n\n"
                "Capturing:\n"
                "- If your last stone lands in an empty pit on your side,\n"
                "  and the opposite pit holds stones, you capture both.\n"
                "- Captured stones plus your last stone go into your store.\n\n"
                "End of the Game:\n"
                "- The game ends when one player's six pits are all empty.\n"
                "- The other player collects all stones remaining on their side.\n"
                "- The player with the most stones in their store wins.\n"
            )
        )
        rules_text.config(state="disabled")

        close_button = tk.Button(
            outer,
            text="Close",
            font=("Helvetica", 12, "bold"),
            padx=10,
            pady=5,
            command=rules_win.destroy,
        )
        close_button.pack(pady=(10, 0))

   
    # -------- build UI --------

    root = tk.Tk()
    root.title("Mancala – Singleplayer")
    root.geometry("980x640")
    root.minsize(900, 600)
    root.configure(bg=bg_color)

    # top bar
    top_frame = tk.Frame(root, bg=bg_color)
    top_frame.pack(fill="x", padx=20, pady=10)

    title_label = tk.Label(
        top_frame,
        text="Mancala (Singleplayer)",
        font=("Helvetica", 24, "bold"),
        fg=text_color,
        bg=bg_color,
    )
    title_label.pack(side="left")

    right_button_frame = tk.Frame(top_frame, bg=bg_color)
    right_button_frame.pack(side="right")

    main_menu_button = tk.Button(
        right_button_frame,
        text="Main Menu",
        font=("Helvetica", 11, "bold"),
        padx=10,
        pady=5,
        command=go_to_main_menu,
    )
    main_menu_button.pack(pady=(0, 8))

    rules_button = tk.Button(
        right_button_frame,
        text="Rules",
        font=("Helvetica", 11, "bold"),
        padx=10,
        pady=5,
        command=show_rules,
    )
    rules_button.pack()

    # center area
    center_frame = tk.Frame(root, bg=bg_color)
    center_frame.pack(fill="both", expand=True, padx=20, pady=10)

    p_ai_label = tk.Label(
        center_frame,
        text="AI (Top Row)",
        font=("Helvetica", 14, "bold"),
        fg=turn_inactive_color,
        bg=bg_color,
    )
    p_ai_label.pack(pady=(0, 8))

    board_outer = tk.Frame(
        center_frame,
        bg=board_bg,
        bd=4,
        relief="ridge",
        padx=15,
        pady=15,
    )
    board_outer.pack(expand=True)

    board_frame = tk.Frame(board_outer, bg=board_bg)
    board_frame.pack()

    # left store = AI (top)
    store_ai_label = tk.Label(
        board_frame,
        text="0",
        width=5,
        relief="groove",
        font=("Helvetica", 14, "bold"),
        bg=store_bg_ai,
        fg=pit_fg,
        padx=5,
        pady=10,
    )
    store_ai_label.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky="ns")

    # AI top pits 12..7 (non-clickable)
    for col, idx in enumerate(top_indices):
        pit_button = tk.Button(
            board_frame,
            text="4",
            width=5,
            font=("Helvetica", 14, "bold"),
            bg=pit_bg_ai,
            fg=pit_fg,
            relief="raised",
            bd=3,
            activebackground=pit_bg_ai,
            activeforeground=pit_fg,
            state="disabled",
        )
        pit_button.grid(row=0, column=1 + col, padx=6, pady=6, ipadx=4, ipady=4)
        top_pit_buttons.append(pit_button)

    # spacers
    for col in range(6):
        spacer = tk.Label(board_frame, text=" ", width=5, bg=board_bg)
        spacer.grid(row=1, column=1 + col)

    # bottom pits: player 0..5 (clickable)
    for col, idx in enumerate(bottom_indices):
        pit_button = tk.Button(
            board_frame,
            text="4",
            width=5,
            font=("Helvetica", 14, "bold"),
            bg=pit_bg_you,
            fg=pit_fg,
            relief="raised",
            bd=3,
            activebackground=pit_bg_you,
            activeforeground=pit_fg,
            command=lambda pit=idx: human_move(pit),
        )
        pit_button.grid(row=2, column=1 + col, padx=6, pady=6, ipadx=4, ipady=4)
        bottom_pit_buttons.append(pit_button)

    # right store = player (bottom)
    store_you_label = tk.Label(
        board_frame,
        text="0",
        width=5,
        relief="groove",
        font=("Helvetica", 14, "bold"),
        bg=store_bg_you,
        fg=pit_fg,
        padx=5,
        pady=10,
    )
    store_you_label.grid(row=0, column=7, rowspan=3, padx=10, pady=5, sticky="ns")

    p_you_label = tk.Label(
        center_frame,
        text="You (Bottom Row)",
        font=("Helvetica", 14, "bold"),
        fg=turn_highlight_color,
        bg=bg_color,
    )
    p_you_label.pack(pady=(8, 0))

    # controls row
    controls_frame = tk.Frame(root, bg=bg_color)
    controls_frame.pack(fill="x", padx=20, pady=(0, 5))

    depth_label = tk.Label(
        controls_frame,
        text=f"Depth: {ai.depth}",
        font=("Helvetica", 12, "bold"),
        fg=text_color,
        bg=bg_color,
    )
    depth_label.pack(side="left")

    btn_frame = tk.Frame(controls_frame, bg=bg_color)
    btn_frame.pack(side="right")

    undo_btn = tk.Button(
        btn_frame,
        text="Undo (u)",
        font=("Helvetica", 11),
        padx=6,
        command=do_undo,
    )
    undo_btn.pack(side="left", padx=4)

    redo_btn = tk.Button(
        btn_frame,
        text="Redo (r)",
        font=("Helvetica", 11),
        padx=6,
        command=do_redo,
    )
    redo_btn.pack(side="left", padx=4)

    hint_btn = tk.Button(
        btn_frame,
        text="Hint (g)",
        font=("Helvetica", 11),
        padx=6,
        command=do_hint,
    )
    hint_btn.pack(side="left", padx=4)

    new_btn = tk.Button(
        btn_frame,
        text="New (n)",
        font=("Helvetica", 11),
        padx=6,
        command=new_game,
    )
    new_btn.pack(side="left", padx=4)

    depth_minus_btn = tk.Button(
        btn_frame,
        text="Depth- (-)",
        font=("Helvetica", 11),
        padx=6,
        command=lambda: do_depth(-1),
    )
    depth_minus_btn.pack(side="left", padx=4)

    depth_plus_btn = tk.Button(
        btn_frame,
        text="Depth+ (+)",
        font=("Helvetica", 11),
        padx=6,
        command=lambda: do_depth(+1),
    )
    depth_plus_btn.pack(side="left", padx=4)

    # status + log
    status_label = tk.Label(
        root,
        text="",
        font=("Helvetica", 13),
        fg=text_color,
        bg=bg_color,
    )
    status_label.pack(pady=(0, 8))

    log_frame = tk.Frame(root, bg=bg_color)
    log_frame.pack(fill="both", expand=False, padx=20, pady=(0, 15))

    log_label = tk.Label(
        log_frame,
        text="Messages:",
        font=("Helvetica", 12, "bold"),
        fg=text_color,
        bg=bg_color,
    )
    log_label.pack(anchor="w")

    log_text = tk.Text(
        log_frame,
        height=6,
        state="disabled",
        wrap="word",
        bg="#202235",
        fg=text_color,
        relief="sunken",
        bd=2,
    )
    log_text.pack(fill="both", expand=True)

    # keyboard shortcuts
    def on_key(event):
        key = event.keysym
        if key in ("u", "U"):
            do_undo()
        elif key in ("r", "R"):
            do_redo()
        elif key in ("g", "G"):
            do_hint()
        elif key in ("n", "N"):
            new_game()
        elif key in ("plus", "KP_Add"):
            do_depth(+1)
        elif key in ("minus", "KP_Subtract"):
            do_depth(-1)
        elif key in ("m", "M"):
            go_to_main_menu()

    root.bind("<Key>", on_key)

    # initial draw
    log("Singleplayer Mancala started. You are the bottom row (Player A).")
    refresh_board()

    root.mainloop()
