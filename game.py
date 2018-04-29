import random

class Game:
    def __init__(self, board):
        self.wall = 'O'
        self.empty = ' '
        self.player = 'X'
        self.num_rows = len(board)
        self.num_cols = len(board[0])
        self.board = board

    def print_board(self):
        for row in self.board:
            for sq in row:
                print(sq, end='')

    def random_empty_location(self):
        while True:
            r = random.randint(0, self.num_rows - 1)
            c = random.randint(0, self.num_cols - 1)
            if self.board[r][c] != self.wall:
                return (r, c)

    def spawn_player(self):
        r, c = self.random_empty_location()
        self.board[r][c] = self.player

    def start_game(self):
        self.spawn_player()

        self.print_board()

def main():
    board = []
    with open('board.txt', 'r') as f:
        for line in f:
            board.append(list(line))
    game = Game(board)
    game.start_game()

if __name__ == '__main__':
    main()
