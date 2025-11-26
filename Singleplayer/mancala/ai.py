from dataclasses import dataclass
from typing import Optional, Tuple
import math
from .rules import pit_range, own_store, other
from .board import Board
from .tt import Zobrist

@dataclass
class SearchResult:
    value: float
    move: Optional[int]
    nodes: int

class AI:
    def __init__(self, depth: int = 6, use_tt: bool = True):
        self.depth = depth
        self.use_tt = use_tt
        self.tt = {}  # (hash, depth) -> (flag, value)
        self.zob = Zobrist()

    def evaluate(self, b: Board, player: int) -> float:
        my_store = b.score(player)
        opp_store_ = b.score(other(player))
        store_diff = my_store - opp_store_
        my_moves = len([i for i in pit_range(player) if b.pits[i] > 0])
        opp_moves = len([i for i in pit_range(other(player)) if b.pits[i] > 0])
        near = sum(b.pits[i] for i in pit_range(player) if (own_store(player) - i) % 14 <= 3)
        return 3.0*store_diff + 0.3*(my_moves - opp_moves) + 0.05*near

    def greedy_hint(self, b: Board) -> Optional[int]:
        best, best_val = None, -math.inf
        for m in b.legal_moves():
            tmp = b.clone()
            tmp.apply_move(m)
            v = self.evaluate(tmp, b.current)
            if v > best_val:
                best_val, best = v, m
        return best

    def minimax(self, b: Board, depth: int, alpha: float, beta: float, root: int) -> Tuple[float, Optional[int], int]:
        nodes = 0

        def _search(state: Board, d: int, a: float, bt: float) -> float:
            nonlocal nodes
            nodes += 1
            if d == 0 or state.terminal():
                return self.evaluate(state, root)

            moves = state.legal_moves()
            if not moves:
                return self.evaluate(state, root)

            def score_move(m):
                tmp = state.clone()
                tmp.apply_move(m)
                return self.evaluate(tmp, root)
            moves.sort(key=score_move, reverse=True)

            maximizing = (state.current == root)
            val = -math.inf if maximizing else math.inf

            if self.use_tt:
                h = self.zob.hash(state)
                key = (h, d)
                if key in self.tt:
                    flag, v = self.tt[key]
                    if flag == 0: return v
                    if flag < 0 and v <= a: return v
                    if flag > 0 and v >= bt: return v

            for m in moves:
                child = state.clone()
                extra, _ = child.apply_move(m)
                nd = d if extra else d - 1
                v = _search(child, nd, a, bt)
                if maximizing:
                    if v > val: val = v
                    if val > a: a = val
                    if a >= bt: break
                else:
                    if v < val: val = v
                    if val < bt: bt = val
                    if a >= bt: break

            if self.use_tt:
                h = self.zob.hash(state)
                key = (h, d)
                flag = 0
                if val <= a: flag = -1
                elif val >= bt: flag = +1
                self.tt[key] = (flag, val)
            return val

        best_move = None
        best_val = -math.inf
        for m in b.legal_moves():
            child = b.clone()
            extra, _ = child.apply_move(m)
            nd = depth if extra else depth - 1
            v = _search(child, nd, alpha, beta)
            if v > best_val:
                best_val, best_move = v, m
        return best_val, best_move, nodes

    def choose(self, b: Board) -> SearchResult:
        if not b.legal_moves():
            return SearchResult(self.evaluate(b, b.current), None, 0)
        val, move, nodes = self.minimax(b, self.depth, -math.inf, math.inf, b.current)
        return SearchResult(val, move, nodes)
