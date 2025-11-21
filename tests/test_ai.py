from mancala.board import Board
from mancala.ai import AI

def test_greedy_hint_runs():
    b = Board.new(4)
    ai = AI(depth=2)
    hint = ai.greedy_hint(b)
    assert hint in range(0,6)

def test_minimax_basic():
    b = Board.new(4)
    ai = AI(depth=4)
    res = ai.choose(b)
    assert res.move in range(0,6)
