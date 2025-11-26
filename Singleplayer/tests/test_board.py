from mancala.board import Board
from mancala.rules import PLAYER_A, A_STORE, B_STORE

def test_new_board_invariants():
    b = Board.new(4)
    assert sum(b.pits) == 48
    assert b.pits[A_STORE] == 0 and b.pits[B_STORE] == 0
    assert b.current == PLAYER_A

def test_legal_moves_start():
    b = Board.new(4)
    assert set(b.legal_moves()) == set(range(0,6))

def test_capture_rule_simple():
    b = Board.new(1)
    b.pits = [0,0,1,0,0,0,0, 0,0,1,0,0,0,0]
    b.current = PLAYER_A
    extra, end = b.apply_move(2)
    assert b.pits[A_STORE] > 0
    assert not extra

def test_end_condition_collect():
    b = Board.new(1)
    b.pits = [0,0,0,0,0,1,0, 0,0,0,0,0,0,0]
    b.current = PLAYER_A
    b.apply_move(5)
    assert b.terminal()
