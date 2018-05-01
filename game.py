from enum import Enum
import random
import curses
import copy
import pdb

direction_to_lambda = {
    'w': lambda pos: (pos[0] - 1, pos[1]),
    's': lambda pos: (pos[0] + 1, pos[1]),
    'a': lambda pos: (pos[0], pos[1] - 1),
    'd': lambda pos: (pos[0], pos[1] + 1),
}

WALL = 'O'
PLAYER = 'X'
EMPTY = ' '
LITTLE_DOT = '.'
BIG_DOT = 'o'

class Game:
    def __init__(self):
        self.board = []
        with open('board.txt', 'r') as f:
            for line in f:
                self.board.append(list(line))
        self.num_rows = len(self.board)
        self.num_cols = len(self.board[0])
        self.fill_board_with_dots()

        # map from player object to their score
        self.leaderboard = {}

    def fill_board_with_dots(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.board[r][c] == EMPTY:
                    if random.randint(1, 100) <= 3:
                        self.board[r][c] = BIG_DOT
                    # else:
                        # self.board[r][c] = LITTLE_DOT

    def print_board(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                print(self.board[r][c], end='')

    def random_empty_location(self):
        while True:
            r = random.randint(0, self.num_rows - 1)
            c = random.randint(0, self.num_cols - 1)
            if self.board[r][c] == EMPTY:
                return (r, c)

    def spawn_player(self, username):
        r, c = self.random_empty_location()
        new_player = Player(self, username, (r,c))
        self.leaderboard[new_player] = 0
        self.board[r][c] = new_player
        return new_player

    # Check if position is in bounds
    def position_is_valid(self, pos):
        row, col = pos

        # Check if out of bounds, or collision
        if (col >= self.num_cols or col < 0 or row >= self.num_rows or row < 0):
            return False
        return True

    # If movable, return number of points from moving to that location
    def position_can_move_to(self, pos):
        if not self.position_is_valid(pos):
            return False

        row, col = pos
        if self.board[row][col] == EMPTY:
            return 0
        elif self.board[row][col] == LITTLE_DOT:
            return 1
        elif self.board[row][col] == BIG_DOT:
            return 10

        return False

    def move_player(self, player):
        row, col = player.position # most definitely bad design lol fix this later
        new_pos = direction_to_lambda[player.direction]((row, col))

        score = self.position_can_move_to(new_pos)
        if score is not False:
            player.position = new_pos
            new_row, new_col = new_pos

            self.board[row][col] = EMPTY
            self.board[new_row][new_col] = player
            self.leaderboard[player] += score

    def remove_player(self, player):
        row, col = player.position
        self.board[row][col] = EMPTY
        del self.leaderboard[player]

    def tick(self):
        for player in self.leaderboard:
            self.move_player(player)


class Player:
    def __init__(self, game, username, pos):
        self.game = game
        self.username = username
        self.position = pos
        self.direction = 'd'

    def change_direction(self, direction):
        assert direction in direction_to_lambda, 'Invalid direction'
        self.direction = direction

    def __repr__(self):
        return self.username[0]


def run_screen(stdscr):
    # Clear screen
    stdscr.clear()
    # Proceed with your program
    stdscr.refresh()
    stdscr.getkey()
    print("Running some program")

# def main():
#     curses.wrapper(run_screen)

# def main():
    # game = load_new_game()
    # game.start_game()

# if __name__ == '__main__':
    # main()
