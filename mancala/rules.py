PITS_PER_SIDE = 6
TOTAL_PITS = 2 * PITS_PER_SIDE + 2  # 14
A_STORE = PITS_PER_SIDE             # 6
B_STORE = TOTAL_PITS - 1            # 13
PLAYER_A, PLAYER_B = 0, 1

def other(player: int) -> int:
    return PLAYER_B if player == PLAYER_A else PLAYER_A

def pit_range(player: int) -> range:
    return range(0, PITS_PER_SIDE) if player == PLAYER_A else range(PITS_PER_SIDE + 1, PITS_PER_SIDE + 1 + PITS_PER_SIDE)

def is_store(i: int) -> bool:
    return i == A_STORE or i == B_STORE

def own_store(player: int) -> int:
    return A_STORE if player == PLAYER_A else B_STORE

def opp_store(player: int) -> int:
    return B_STORE if player == PLAYER_A else A_STORE

def opposite(i: int) -> int:
    if is_store(i):
        raise ValueError("Stores have no opposite pit")
    return TOTAL_PITS - 2 - i
