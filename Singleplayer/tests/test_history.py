from mancala.board import Board
from mancala.history import History

def test_undo_redo_roundtrip():
    b = Board.new(4)
    h = History()
    h.push(b)
    b.apply_move(0)
    assert h.undo(b) is True
    assert h.redo(b) is True
