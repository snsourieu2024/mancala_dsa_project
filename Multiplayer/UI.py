import tkinter as tk
from tkinter import messagebox
from game import Game as BaseGame
import sys
import subprocess
import os


class MancalaGame(BaseGame):

    def __init__(self):
        self.board_1 = [4, 4, 4, 4, 4, 4, 0]
        self.board_2 = [4, 4, 4, 4, 4, 4, 0]
        self.turn = 1

    def end_game(self):
        ended_player = None

        if sum(self.board_1[:6]) == 0:
            self.board_2[6] += sum(self.board_2[:6])
            for i in range(6):
                self.board_2[i] = 0
            ended_player = 1
        elif sum(self.board_2[:6]) == 0:
            self.board_1[6] += sum(self.board_1[:6])
            for i in range(6):
                self.board_1[i] = 0
            ended_player = 2

        if self.board_1[6] > self.board_2[6]:
            winner = 1
        elif self.board_2[6] > self.board_1[6]:
            winner = 2
        else:
            winner = 0

        return ended_player, winner

    def apply_move(self, move):
        if move < 0 or move > 5:
            return False, "Enter integer value between 1 and 6.", False, False, None

        if self.turn == 1:
            if self.board_1[move] == 0:
                return False, "Choose a cell with at least one pebble.", False, False, None
        else:
            if self.board_2[move] == 0:
                return False, "Choose a cell with at least one pebble.", False, False, None

        cell = move
        temp = 0

        if self.turn == 1:
            while self.board_1[move]:
                cell += 1
                if cell % 14 == move:
                    temp += 1
                    self.board_1[move] -= 1
                elif cell // 7 % 2 == 0:
                    self.board_1[cell % 7] += 1
                    self.board_1[move] -= 1
                elif (cell - 13) % 14 != 0:
                    self.board_2[cell % 7] += 1
                    self.board_1[move] -= 1
            self.board_1[move] = temp
        else:
            while self.board_2[move]:
                cell += 1
                if cell % 14 == move:
                    temp += 1
                    self.board_2[move] -= 1
                elif cell // 7 % 2 == 0:
                    self.board_2[cell % 7] += 1
                    self.board_2[move] -= 1
                elif (cell - 13) % 14 != 0:
                    self.board_1[cell % 7] += 1
                    self.board_2[move] -= 1
            self.board_2[move] = temp

        self.eat_pebbles(cell)

        game_over = False
        winner = None
        extra_turn = False
        message_lines = []

        if sum(self.board_1[:6]) == 0 or sum(self.board_2[:6]) == 0:
            ended_player, winner = self.end_game()
            game_over = True

            if ended_player == 1:
                message_lines.append(
                    "Player 1 has no pebbles left, and Player 2 collects all its pebbles."
                )
            elif ended_player == 2:
                message_lines.append(
                    "Player 2 has no pebbles left, and Player 1 collects all its pebbles."
                )

            if winner == 0:
                message_lines.append(
                    "The match is a tie as both players have 24 pebbles!"
                )
            else:
                pebbles = self.board_1[6] if winner == 1 else self.board_2[6]
                message_lines.append(
                    f"Player {winner} wins the match with {pebbles} pebbles!"
                )
        else:
            if (cell - 6) % 14 == 0:
                extra_turn = True
            else:
                self.change_turn()

        message = "\n".join(message_lines)
        return True, message, extra_turn, game_over, winner


class MancalaUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mancala")
        self.root.geometry("900x600")
        self.root.minsize(900, 600)

        self.bg_color = "#151726"
        self.board_bg = "#262b3f"
        self.store_bg_p1 = "#4f9cff"
        self.store_bg_p2 = "#ffb347"
        self.pit_bg_p1 = "#3b78d8"
        self.pit_bg_p2 = "#f4c95d"
        self.pit_fg = "#ffffff"
        self.text_color = "#f0f0f0"
        self.turn_highlight_color = "#ffffff"
        self.turn_inactive_color = "#888888"

        self.root.configure(bg=self.bg_color)

        self.game = MancalaGame()

        self.top_pit_buttons = []
        self.bottom_pit_buttons = []
        self.store1_label = None
        self.store2_label = None

        self._build_layout()
        self._refresh_board()
        self._log("Player 1 starts. Click one of Player 1's pits.")

    def _build_layout(self):
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill="x", padx=20, pady=10)

        title_label = tk.Label(
            top_frame,
            text="Mancala (Multiplayer)",
            font=("Helvetica", 24, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
        )
        title_label.pack(side="left")

        right_button_frame = tk.Frame(top_frame, bg=self.bg_color)
        right_button_frame.pack(side="right")

        main_menu_button = tk.Button(
            right_button_frame,
            text="Main Menu",
            font=("Helvetica", 11, "bold"),
            padx=10,
            pady=5,
            command=self._go_back_to_menu,
        )
        main_menu_button.pack(pady=(0, 8))

        rules_button = tk.Button(
            right_button_frame,
            text="Rules",
            font=("Helvetica", 11, "bold"),
            padx=10,
            pady=5,
            command=self._show_rules,
        )
        rules_button.pack()

        center_frame = tk.Frame(self.root, bg=self.bg_color)
        center_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.p1_label = tk.Label(
            center_frame,
            text="Player 1 (Top Row)",
            font=("Helvetica", 14, "bold"),
            fg=self.turn_highlight_color,
            bg=self.bg_color,
        )
        self.p1_label.pack(pady=(0, 8))

        board_outer = tk.Frame(
            center_frame,
            bg=self.board_bg,
            bd=4,
            relief="ridge",
            padx=15,
            pady=15,
        )
        board_outer.pack(expand=True)

        board_frame = tk.Frame(board_outer, bg=self.board_bg)
        board_frame.pack()

        self.store1_label = tk.Label(
            board_frame,
            text="0",
            width=5,
            relief="groove",
            font=("Helvetica", 14, "bold"),
            bg=self.store_bg_p1,
            fg=self.pit_fg,
            padx=5,
            pady=10,
        )
        self.store1_label.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky="ns")

        self.store2_label = tk.Label(
            board_frame,
            text="0",
            width=5,
            relief="groove",
            font=("Helvetica", 14, "bold"),
            bg=self.store_bg_p2,
            fg=self.pit_fg,
            padx=5,
            pady=10,
        )
        self.store2_label.grid(row=0, column=7, rowspan=3, padx=10, pady=5, sticky="ns")

        for col in range(6):
            pit_button = tk.Button(
                board_frame,
                text="4",
                width=5,
                font=("Helvetica", 14, "bold"),
                bg=self.pit_bg_p1,
                fg=self.pit_fg,
                relief="raised",
                bd=3,
                activebackground=self.pit_bg_p1,
                activeforeground=self.pit_fg,
                command=lambda c=col: self._pit_clicked(player=1, pit_index=5 - c),
            )
            pit_button.grid(row=0, column=1 + col, padx=6, pady=6, ipadx=4, ipady=4)
            self.top_pit_buttons.append(pit_button)

        for col in range(6):
            spacer = tk.Label(board_frame, text=" ", width=5, bg=self.board_bg)
            spacer.grid(row=1, column=1 + col)

        for col in range(6):
            pit_button = tk.Button(
                board_frame,
                text="4",
                width=5,
                font=("Helvetica", 14, "bold"),
                bg=self.pit_bg_p2,
                fg=self.pit_fg,
                relief="raised",
                bd=3,
                activebackground=self.pit_bg_p2,
                activeforeground=self.pit_fg,
                command=lambda c=col: self._pit_clicked(player=2, pit_index=c),
            )
            pit_button.grid(row=2, column=1 + col, padx=6, pady=6, ipadx=4, ipady=4)
            self.bottom_pit_buttons.append(pit_button)

        self.p2_label = tk.Label(
            center_frame,
            text="Player 2 (Bottom Row)",
            font=("Helvetica", 14, "bold"),
            fg=self.turn_inactive_color,
            bg=self.bg_color,
        )
        self.p2_label.pack(pady=(8, 0))

        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 13),
            fg=self.text_color,
            bg=self.bg_color,
        )
        self.status_label.pack(pady=(0, 8))

        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(fill="both", expand=False, padx=20, pady=(0, 15))

        log_label = tk.Label(
            log_frame,
            text="Messages:",
            font=("Helvetica", 12, "bold"),
            fg=self.text_color,
            bg=self.bg_color,
        )
        log_label.pack(anchor="w")

        self.log_text = tk.Text(
            log_frame,
            height=6,
            state="disabled",
            wrap="word",
            bg="#202235",
            fg=self.text_color,
            relief="sunken",
            bd=2,
        )
        self.log_text.pack(fill="both", expand=True)

    def _show_rules(self):
        rules_win = tk.Toplevel(self.root)
        rules_win.title("Mancala – Rules")
        rules_win.configure(bg=self.bg_color)
        rules_win.geometry("520x520")
        rules_win.resizable(False, False)

        outer = tk.Frame(
            rules_win,
            bg=self.board_bg,
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
            bg=self.board_bg,
        )
        title.pack(pady=(0, 15))

        text_frame = tk.Frame(outer, bg=self.board_bg)
        text_frame.pack(expand=True, fill="both")

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        rules_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Helvetica", 12),
            bg=self.board_bg,
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
                "- Each player owns the six pits on their side of the board.\n"
                "- Player 1 is the TOP row. Player 2 is the BOTTOM row.\n"
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

    def _go_back_to_menu(self):
        self.root.destroy()

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        play_path = os.path.join(base_dir, "play.py")

        subprocess.Popen([sys.executable, play_path], cwd=base_dir)

    def _pit_clicked(self, player, pit_index):
        if self.game.turn != player:
            self._log(f"It's Player {self.game.turn}'s turn.")
            return

        ok, message, extra_turn, game_over, winner = self.game.apply_move(pit_index)

        if not ok:
            if message:
                self._log(message)
            return

        self._refresh_board()

        if message:
            self._log(message)

        if game_over:
            if winner == 0:
                self.status_label.config(text="Game over: it's a tie!")
            else:
                self.status_label.config(text=f"Game over: Player {winner} wins!")
            self._disable_pits()
        else:
            if extra_turn:
                self.status_label.config(
                    text=f"Player {player} gets another turn."
                )
            else:
                self.status_label.config(
                    text=f"Player {self.game.turn}'s turn."
                )

    def _refresh_board(self):
        b1 = self.game.board_1
        b2 = self.game.board_2

        for col, button in enumerate(self.top_pit_buttons):
            index = 5 - col
            button.config(text=str(b1[index]), bg=self.pit_bg_p1, fg=self.pit_fg)

        for col, button in enumerate(self.bottom_pit_buttons):
            index = col
            button.config(text=str(b2[index]), bg=self.pit_bg_p2, fg=self.pit_fg)

        self.store1_label.config(text=str(b1[6]), bg=self.store_bg_p1, fg=self.pit_fg)
        self.store2_label.config(text=str(b2[6]), bg=self.store_bg_p2, fg=self.pit_fg)

        if self.game.turn == 1:
            self.p1_label.config(fg=self.turn_highlight_color)
            self.p2_label.config(fg=self.turn_inactive_color)
            for btn in self.top_pit_buttons:
                btn.config(relief="raised", bd=4)
            for btn in self.bottom_pit_buttons:
                btn.config(relief="sunken", bd=2)
        else:
            self.p1_label.config(fg=self.turn_inactive_color)
            self.p2_label.config(fg=self.turn_highlight_color)
            for btn in self.bottom_pit_buttons:
                btn.config(relief="raised", bd=4)
            for btn in self.top_pit_buttons:
                btn.config(relief="sunken", bd=2)

    def _disable_pits(self):
        for btn in self.top_pit_buttons + self.bottom_pit_buttons:
            btn.config(state="disabled")

    def _log(self, text):
        if not text:
            return
        self.log_text.config(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")


def main():
    root = tk.Tk()
    app = MancalaUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
