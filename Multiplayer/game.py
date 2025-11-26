
#     6    5  4  3  2  1  0
#            <- Player 1 <-
#   /   \ [4][4][4][4][4][4] /   \
#   | 0 |                    | 0 |
#   \   / [4][4][4][4][4][4] \   /
#            -> Player 2 ->
#          0  1  2  3  4  5    6

from time import sleep

class Game:
    def __init__(self):
        self.board_1 = [4, 4, 4, 4, 4, 4, 0]
        self.board_2 = [4, 4, 4, 4, 4, 4, 0]
        self.turn = 1
        Game.print_board(self)
        Game.turns(self)

    def print_board(self):
        print(f'        <- Player 1 <-\n'
              f'       6  5  4  3  2  1\n'
              f'|   | [{self.board_1[5]}][{self.board_1[4]}][{self.board_1[3]}][{self.board_1[2]}][{self.board_1[1]}][{self.board_1[0]}] |   |\n'
              f'| {self.board_1[6]} |                    | {self.board_2[6]} |\n'
              f'|   | [{self.board_2[0]}][{self.board_2[1]}][{self.board_2[2]}][{self.board_2[3]}][{self.board_2[4]}][{self.board_2[5]}] |   |\n'
              f'       1  2  3  4  5  6\n'
              f'        -> Player 2 ->\n')

    def turns(self):
        while self.turn:
            try:
                move = int(input(f'Player {self.turn}\nEnter move: ')) - 1
                if move < 0 or move > 5:
                    print('Enter integer value between 1 and 6')
                    continue
                if self.turn == 1:
                    if self.board_1[move] == 0:
                        print('Choose a cell with at least one pebble')
                        continue
                else:
                    if self.board_2[move] == 0:
                        print('Choose a cell with at least one pebble')
                        continue
            except ValueError:
                print('Enter integer value between 1 and 6')
                continue
            print('\n')
            cell = move
            temp = 0
            if self.turn == 1:
                while self.board_1[move]:
                    cell += 1
                    if cell%14 == move:
                        temp += 1
                        self.board_1[move] -= 1
                    elif cell//7%2 == 0:
                        self.board_1[cell%7] += 1
                        self.board_1[move] -= 1
                    elif (cell-13)%14 != 0:
                        self.board_2[cell%7] += 1
                        self.board_1[move] -= 1
                self.board_1[move] = temp
            else:
                while self.board_2[move]:
                    cell += 1
                    if cell%14 == move:
                        temp += 1
                        self.board_2[move] -= 1
                    elif cell//7%2 == 0:
                        self.board_2[cell%7] += 1
                        self.board_2[move] -= 1
                    elif (cell-13)%14 != 0:
                        self.board_1[cell%7] += 1
                        self.board_2[move] -= 1
                self.board_2[move] = temp

            Game.eat_pebbles(self, cell)

            Game.print_board(self)
            if sum(self.board_1[:6]) == 0 or sum(self.board_2[:6]) == 0:
                Game.end_game(self)
                self.turn = 0
            elif (cell-6)%14 != 0:
                Game.change_turn(self)

            sleep(3)

    def change_turn(self):
        if self.turn == 1:
            self.turn = 2
        else:
            self.turn = 1

    def eat_pebbles(self, cell):
        if cell//7%2 == 0 and cell%7 != 6:
            if self.turn == 1:
                if self.board_1[cell%7] == 1 and self.board_2[abs((cell%7) - 5)] != 0:
                    self.board_1[6] += self.board_2[abs((cell%7) - 5)] + 1
                    self.board_1[cell%7] = 0
                    self.board_2[abs((cell % 7) - 5)] = 0
            else:
                if self.board_2[cell%7] == 1 and self.board_1[abs((cell%7) - 5)] != 0:
                    self.board_2[6] += self.board_1[abs((cell % 7) - 5)] + 1
                    self.board_2[cell % 7] = 0
                    self.board_1[abs((cell % 7) - 5)] = 0

    def end_game(self):
        sleep(2)
        if sum(self.board_1[:6]) == 0:
            print('Player 1 has no pebbles left, and Player 2 collects all its pebbles\n')
            self.board_2[6] += sum(self.board_2[:6])
            for i in range(6):
                self.board_2[i] = 0

        else:
            print('Player 2 has no pebbles left, and Player 1 collects all its pebbles\n')
            self.board_1[6] += sum(self.board_1[:6])
            for i in range(6):
                self.board_1[i] = 0
        sleep(2)
        Game.print_board(self)
        sleep(1)

        if self.board_1[6] != self.board_2[6]:
            print(f'{'Player 1' if self.board_1[6] > self.board_2[6] else 'Player 2'} wins the match '
              f'with {self.board_1[6] if self.board_1[6] > self.board_2[6] else self.board_2[6]} pebbles!')
        else:
            print(f'The match is a tie as both players have 24 pebbles!')


if __name__ == "__main__":
    Game()
