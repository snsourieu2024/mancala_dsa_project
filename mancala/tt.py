import random
from .rules import TOTAL_PITS, PLAYER_B

class Zobrist:
    def __init__(self, seed: int = 12345):
        random.seed(seed)
        self.table = [[random.getrandbits(64) for _ in range(49)] for _ in range(TOTAL_PITS)]
        self.turn_key = random.getrandbits(64)

    def hash(self, board) -> int:
        h = 0
        for i in range(TOTAL_PITS):
            s = board.pits[i]
            s = min(s, 48)
            h ^= self.table[i][s]
        if board.current == PLAYER_B:
            h ^= self.turn_key
        return h
