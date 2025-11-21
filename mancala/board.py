from dataclasses import dataclass
from typing import List, Tuple, Optional
from .rules import (PITS_PER_SIDE, TOTAL_PITS, A_STORE, B_STORE, PLAYER_A, PLAYER_B,
                    pit_range, own_store, opp_store, opposite, other)

@dataclass
class Board:
    pits: List[int]
    current: int = PLAYER_A

    @staticmethod
    def new(start_stones: int = 4) -> "Board":
        pits = [start_stones]*PITS_PER_SIDE + [0] + [start_stones]*PITS_PER_SIDE + [0]
        return Board(pits, PLAYER_A)

    def clone(self) -> "Board":
        return Board(self.pits.copy(), self.current)

    def legal_moves(self) -> List[int]:
        rng = pit_range(self.current)
        return [i for i in rng if self.pits[i] > 0]

    def side_empty(self, player: int) -> bool:
        rng = pit_range(player)
        return all(self.pits[i] == 0 for i in rng)

    def apply_move(self, pit_index: int) -> Tuple[bool, Optional[str]]:
        player = self.current
        if pit_index not in pit_range(player):
            raise AssertionError("Pit not on current player's side")
        stones = self.pits[pit_index]
        if stones == 0:
            raise ValueError("Illegal move: empty pit")
        self.pits[pit_index] = 0

        idx = pit_index
        while stones > 0:
            idx = (idx + 1) % TOTAL_PITS
            if idx == opp_store(player):
                continue
            self.pits[idx] += 1
            stones -= 1

        extra_turn = (idx == own_store(player))

        # Capture
        if (not extra_turn) and (idx in pit_range(player)) and self.pits[idx] == 1:
            opp_idx = opposite(idx)
            captured = self.pits[opp_idx]
            if captured > 0:
                self.pits[own_store(player)] += captured + 1
                self.pits[idx] = 0
                self.pits[opp_idx] = 0

        end_reason = None
        if self.side_empty(PLAYER_A) or self.side_empty(PLAYER_B):
            for i in pit_range(PLAYER_A):
                self.pits[A_STORE] += self.pits[i]
                self.pits[i] = 0
            for i in pit_range(PLAYER_B):
                self.pits[B_STORE] += self.pits[i]
                self.pits[i] = 0
            end_reason = "side_empty"

        if not extra_turn and end_reason is None:
            self.current = other(player)
        return extra_turn, end_reason

    def score(self, player: int) -> int:
        return self.pits[own_store(player)]

    def terminal(self) -> bool:
        nonstores = sum(self.pits[i] for i in range(TOTAL_PITS) if i not in (A_STORE, B_STORE))
        return nonstores == 0

    def as_tuple(self):
        return tuple(self.pits) + (self.current,)
