from typing import List, Tuple
from .board import Board

class History:
    def __init__(self):
        self.undo_stack: List[Tuple[list[int], int]] = []
        self.redo_stack: List[Tuple[list[int], int]] = []

    def push(self, board: Board) -> None:
        self.undo_stack.append((board.pits.copy(), board.current))
        self.redo_stack.clear()

    def undo(self, board: Board) -> bool:
        if not self.undo_stack:
            return False
        self.redo_stack.append((board.pits.copy(), board.current))
        pits, cur = self.undo_stack.pop()
        board.pits = pits
        board.current = cur
        return True

    def redo(self, board: Board) -> bool:
        if not self.redo_stack:
            return False
        self.undo_stack.append((board.pits.copy(), board.current))
        pits, cur = self.redo_stack.pop()
        board.pits = pits
        board.current = cur
        return True
