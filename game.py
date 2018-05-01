from enum import Enum
import random
import curses
from operator import itemgetter
import copy
import pdb

direction_to_lambda = {
    'w': lambda pos: (pos[0] - 1, pos[1]),
    's': lambda pos: (pos[0] + 1, pos[1]),
    'a': lambda pos: (pos[0], pos[1] - 1),
    'd': lambda pos: (pos[0], pos[1] + 1),
}

WALL = 'O'
EMPTY = ' '
LITTLE_DOT = '.'
BIG_DOT = 'o'

class Game:
    def __init__(self):
        self.board = []
        with open('board2.txt', 'r') as f:
            for line in f:
                self.board.append(list(line.rstrip('\n')))
        self.num_rows = len(self.board)
        self.num_cols = len(self.board[0])
        self.n_big_dots = 0
        self.fill_board_with_dots()

        # map from player object to their score
        self.leaderboard = {}
        # game time
        self.ticks = 0

    def fill_board_with_dots(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.board[r][c] == EMPTY:
                    if random.randint(1, 100) <= 3:
                        self.board[r][c] = BIG_DOT
                        self.n_big_dots += 1
                    # else:
                        # self.board[r][c] = LITTLE_DOT

    def draw_leaderboard(self, scr):
        sorted_leaderboard = sorted(self.leaderboard.items(), key=itemgetter(1))

        for i, (username, points) in enumerate(sorted_leaderboard):
            display_string = "{} : {} points".format(username, points)
            scr.addstr(self.num_rows+i, 0, display_string)

    # Print stretching out column-wise by factor of 2, length-wise by factor of 3
    def draw_board(self, scr):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                char_print = str(self.board[r][c])
                if self.board[r][c] == WALL:
                    # Yes, that's a wall
                    char_print = chr(9608)

                for i in range(2):
                    for j in range(3):
                        scr.addstr(r * 2 + i, c * 3 + j, char_print)

    def draw_screen(self, scr):
        self.draw_board(scr)
        self.draw_leaderboard(scr)

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

    def wrap_pos(self, pos):
        row, col = pos
        print(self.num_cols)
        return (row % self.num_rows, col % self.num_cols)

    # Check if position is in bounds
    def position_is_valid(self, pos):
        row, col = pos

        # Check if out of bounds, or collision
        if (col >= self.num_cols or col < 0 or row >= self.num_rows or row < 0):
            return False
        return True

    # If movable, return number of points from moving to that location
    def position_can_move_to(self, player, pos):
        if not self.position_is_valid(pos):
            return False

        row, col = pos
        square = self.board[row][col]
        if square == EMPTY:
            return 0
        elif square == LITTLE_DOT:
            return 1
        elif square == BIG_DOT:
            return 10
        elif isinstance(square, Player):
            if player.superspeed_ticks > 0:
            # TODO: Right now, the "earlier" player in the leaderboard kills the later one.
                square.alive = False
                return 100

        return False

    def process_squares(self, old, new, player):
        if new == BIG_DOT:
            player.superspeed_ticks = 10

    def restart_player(self, player):
        old_r, old_c = player.position
        self.board[old_r][old_c] = EMPTY

        new_r, new_c = self.random_empty_location()
        self.board[new_r][new_c] = player
        player.position = new_r, new_c

        # Reset to zero
        self.leaderboard[player] = 0
        player.alive = True


    def move_player(self, player):
        if player.superspeed_ticks == 0 and self.ticks % 2 == 1:
            return

        row, col = player.position # most definitely bad design lol fix this later
        new_pos = direction_to_lambda[player.direction]((row, col))
        new_pos = self.wrap_pos(new_pos)

        score = self.position_can_move_to(player, new_pos)
        if score is not False:
            player.position = new_pos
            new_row, new_col = new_pos

            self.process_squares(self.board[row][col], self.board[new_row][new_col], player)
            self.board[row][col] = EMPTY
            self.board[new_row][new_col] = player
            self.leaderboard[player] += score

    def remove_player(self, player):
        row, col = player.position
        self.board[row][col] = EMPTY
        del self.leaderboard[player]

    def tick(self):
        for player in self.leaderboard:
            if player.alive:
                self.move_player(player)
                if player.superspeed_ticks > 0:
                    player.superspeed_ticks -= 1

        if self.n_big_dots < 10:
            self.fill_board_with_dots()

        self.ticks += 1


class Player:
    def __init__(self, game, username, pos):
        self.game = game
        self.username = username
        self.position = pos
        self.direction = 'd'
        self.superspeed_ticks = 0
        self.alive = True

    def change_direction(self, direction):
        assert direction in direction_to_lambda, 'Invalid direction'
        self.direction = direction

    def __str__(self):
        return self.username[0]

    def __repr__(self):
        return self.username


# def main():
    # game = load_new_game()
    # game.start_game()

# if __name__ == '__main__':
    # main()
