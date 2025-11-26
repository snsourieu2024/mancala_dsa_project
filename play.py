import tkinter as tk
from tkinter import messagebox
import sys
import subprocess
import os


class MancalaLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Mancala – Play")
        self.root.geometry("900x600")
        self.root.minsize(900, 600)

        self.bg_color = "#151726"
        self.card_bg = "#262b3f"
        self.text_color = "#f0f0f0"
        self.accent_p1 = "#4f9cff"  # single player accent
        self.accent_p2 = "#ffb347"  # multiplayer accent

        self.root.configure(bg=self.bg_color)

        self._build_layout()

    def _build_layout(self):
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill="x", padx=20, pady=20)

        title_label = tk.Label(
            top_frame,
            text="Mancala",
            font=("Helvetica", 28, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
        )
        title_label.pack(side="left")

        right_top = tk.Frame(top_frame, bg=self.bg_color)
        right_top.pack(side="right")

        subtitle_label = tk.Label(
            right_top,
            text="Choose a mode to play",
            font=("Helvetica", 14),
            fg="#b0b0b0",
            bg=self.bg_color,
        )
        subtitle_label.pack(side="left", padx=(0, 10))

        rules_button = tk.Button(
            right_top,
            text="Rules",
            font=("Helvetica", 11, "bold"),
            padx=10,
            pady=5,
            command=self._show_rules,
        )
        rules_button.pack(side="left")

        center_frame = tk.Frame(self.root, bg=self.bg_color)
        center_frame.pack(expand=True, fill="both", padx=20, pady=10)

        card = tk.Frame(
            center_frame,
            bg=self.card_bg,
            bd=4,
            relief="ridge",
            padx=30,
            pady=30,
        )
        card.pack(expand=True)

        sp_frame = tk.Frame(card, bg=self.card_bg)
        sp_frame.pack(fill="x", pady=15)

        sp_title = tk.Label(
            sp_frame,
            text="Single Player",
            font=("Helvetica", 20, "bold"),
            fg=self.accent_p1,
            bg=self.card_bg,
        )
        sp_title.grid(row=0, column=0, sticky="w")

        sp_button = tk.Button(
            sp_frame,
            text="Play Single Player",
            font=("Helvetica", 14, "bold"),
            padx=18,
            pady=8,
            command=self._launch_singleplayer,
        )
        sp_button.grid(row=0, column=1, padx=(20, 0), sticky="e")

        sp_desc = tk.Label(
            sp_frame,
            text=(
                "• 1 player vs AI\n"
                "• Uses the Single player Mancala engine\n"
                "• Practice strategies and test different openings\n"
            ),
            font=("Helvetica", 12),
            justify="left",
            fg=self.text_color,
            bg=self.card_bg,
        )
        sp_desc.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        sep = tk.Frame(card, height=2, bg="#3c425a")
        sep.pack(fill="x", pady=20)

        mp_frame = tk.Frame(card, bg=self.card_bg)
        mp_frame.pack(fill="x", pady=15)

        mp_title = tk.Label(
            mp_frame,
            text="Multiplayer",
            font=("Helvetica", 20, "bold"),
            fg=self.accent_p2,
            bg=self.card_bg,
        )
        mp_title.grid(row=0, column=0, sticky="w")

        mp_button = tk.Button(
            mp_frame,
            text="Play Multiplayer",
            font=("Helvetica", 14, "bold"),
            padx=18,
            pady=8,
            command=self._launch_multiplayer,
        )
        mp_button.grid(row=0, column=1, padx=(20, 0), sticky="e")

        mp_desc = tk.Label(
            mp_frame,
            text=(
                "• 2 players on the same device\n"
                "• Uses the Multiplayer Mancala game and UI\n"
                "• Great for head-to-head matches and testing tactics with friends\n"
            ),
            font=("Helvetica", 12),
            justify="left",
            fg=self.text_color,
            bg=self.card_bg,
        )
        mp_desc.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        footer = tk.Label(
            self.root,
            text="Tip: you can close this launcher after starting a mode if you only want one window open.",
            font=("Helvetica", 10),
            fg="#a0a0a0",
            bg=self.bg_color,
        )
        footer.pack(pady=(0, 10))


    def _show_rules(self):
        rules_win = tk.Toplevel(self.root)
        rules_win.title("Mancala – Rules")
        rules_win.configure(bg=self.bg_color)
        rules_win.geometry("520x520")
        rules_win.resizable(False, False)

        outer = tk.Frame(
            rules_win,
            bg=self.card_bg,
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
            fg=self.text_color,
            bg=self.card_bg,
        )
        title.pack(pady=(0, 15))

        text_frame = tk.Frame(outer, bg=self.card_bg)
        text_frame.pack(expand=True, fill="both")

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        rules_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Helvetica", 12),
            bg=self.card_bg,
            fg=self.text_color,
            relief="flat",
            yscrollcommand=scrollbar.set,
        )
        rules_text.pack(expand=True, fill="both")

        scrollbar.config(command=rules_text.yview)

        rules_text.insert(
            "end",
            (
                "Basic Mancala Rules:\n\n"
                "Board & Players:\n"
                "- Each player owns the six pits on their side of the board.\n"
                "- Player 1 is the TOP row. Player 2 is the BOTTOM row.\n"
                "- Each player also has a large store on their right.\n\n"
                "Turns & Sowing:\n"
                "- On your turn, choose one of your six pits (not your store).\n"
                "- Pick up all stones from that pit.\n"
                "- Moving counter-clockwise, drop one stone in each pit you pass,\n"
                "  including your own store, but skipping your opponent's store.\n\n"
                "Extra Turn:\n"
                "- If your last stone lands in your own store, you get another turn.\n\n"
                "Capturing:\n"
                "- If your last stone lands in an empty pit on your side and the\n"
                "  opposite pit on your opponent's side has stones, you capture\n"
                "  all stones from that opposite pit plus your last stone.\n"
                "- All captured stones go into your store.\n\n"
                "End of the Game:\n"
                "- The game ends when one player's six pits on their side are empty.\n"
                "- The other player collects all remaining stones on their side.\n"
                "- The player with the most stones in their store wins.\n\n"
                "Modes in this launcher:\n"
                "- Single player: you vs the AI (good for practice).\n"
                "- Multiplayer: two players locally share the same board.\n"
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


    def _launch_singleplayer(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        singleplayer_dir = os.path.join(base_dir, "Singleplayer")

        try:
            subprocess.Popen(
                [sys.executable, "-m", "mancala.main", "--gui"],
                cwd=singleplayer_dir,
            )
        except Exception as e:
            messagebox.showerror(
                "Error launching Single player",
                f"Could not start single player mode.\n\n{e}",
            )
            return

        self.root.destroy()

    def _launch_multiplayer(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, "Multiplayer", "UI.py")

        try:
            subprocess.Popen(
                [sys.executable, ui_path],
                cwd=base_dir,
            )
        except Exception as e:
            messagebox.showerror(
                "Error launching Multiplayer",
                f"Could not start multiplayer mode.\n\n{e}",
            )
            return

        self.root.destroy()


def main():
    root = tk.Tk()
    app = MancalaLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
