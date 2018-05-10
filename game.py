import pdb
import copy
import time
import random
import curses
from enum import IntEnum
from operator import itemgetter

# We encode directions canonically as their letter (w up, s down, a left, d right)
direction_to_lambda = {
    'w': lambda pos: (pos[0] - 1, pos[1]),
    's': lambda pos: (pos[0] + 1, pos[1]),
    'a': lambda pos: (pos[0], pos[1] - 1),
    'd': lambda pos: (pos[0], pos[1] + 1),
}

def opposite_direction(direction):
    """Returns the opposite direction given as a character.

    Args:
        direction: char, representing the input direction. 

    Returns:
        char, representing the opposite direction.
    """
    if direction == 'w':
        return 's'
    if direction == 's':
        return 'w'
    if direction == 'a':
        return 'd'
    if direction == 'd':
        return 'a'

# Our game encodes each square as one of these characters
WALL = 'O'
EMPTY = ' '
BIG_DOT = 'o'

# Character to print to represent an object, looks like: █
BLOCK_PRINT = chr(9608)

class Colors(IntEnum):
    BLACK = 0
    RED = 1
    YELLOW = 2
    BLUE = 3
    CYAN = 4
    MAGENTA = 5

class Game:
    """Class representing game states.
    """
    def __init__(self):
        # 2D array representing the boar
        self.board = []
        with open('board.txt', 'r') as f:
            for line in f:
                self.board.append(list(line.rstrip('\n')))
        self.num_rows = len(self.board)
        self.num_cols = len(self.board[0])
        self.n_big_dots = 0
        self.fill_board_with_dots()

        # map from player username to their score
        self.leaderboard = {}
        # map from player username to their player object
        self.players = {}
        # game time
        self.num_ticks = 0
        # actual clock time
        self.timestamp = 0

    def init_curses(self):
        # Default pair 0: white on black
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    def fill_board_with_dots(self):
        """Randomly fills some elements of the game board with big dots.

        Side effect: modifices self.board
        """
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.board[r][c] == EMPTY:
                    if random.randint(1, 100) <= 3:
                        self.board[r][c] = BIG_DOT
                        self.n_big_dots += 1

    def draw_leaderboard(self, scr):
        """Draws the leaderboard at the bottom of the screen.
        """
        for i, (username, points) in enumerate(self.leaderboard.items()):
            display_string = '{} : {} points'.format(username, points)
            scr.addstr(2 * self.num_rows + i, 0, display_string)

    # Print stretching out column-wise by factor of 2, length-wise by factor of 3
    def draw_board(self, scr, curr_username):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                char_print = str(self.board[r][c])
                color = Colors.BLACK
                square = self.board[r][c]

                if square == WALL:
                    char_print = BLOCK_PRINT
                elif square == BIG_DOT:
                    char_print = BLOCK_PRINT
                    color = Colors.CYAN
                elif isinstance(square, Player):
                    char_print = BLOCK_PRINT
                    if square.username == curr_username:
                        if square.superspeed_ticks:
                            color = Colors.BLUE
                        else:
                            color = Colors.YELLOW
                    else:
                        if square.superspeed_ticks:
                            color = Colors.RED
                        else:
                            color = Colors.MAGENTA

                for i in range(2):
                    for j in range(3):
                        scr.addstr(r * 2 + i, c * 3 + j, char_print,
                            curses.color_pair(int(color)) | curses.A_BLINK)

    def draw_screen(self, scr, curr_username):
        self.draw_board(scr, curr_username)
        self.draw_leaderboard(scr)

    def random_empty_location(self):
        while True:
            r = random.randint(0, self.num_rows - 1)
            c = random.randint(0, self.num_cols - 1)
            if self.board[r][c] == EMPTY:
                return (r, c)

    def wrap_pos(self, pos):
        row, col = pos
        return (row % self.num_rows, col % self.num_cols)

    # Check if position is in bounds
    def position_is_valid(self, pos):
        row, col = pos

        # Check if out of bounds, or collision
        if (col >= self.num_cols or col < 0 or row >= self.num_rows or row < 0):
            return False
        return True

    # Returns a tuple (pos is movable, # of points gained OR None)
    def position_can_move_to(self, player, pos):
        if not self.position_is_valid(pos):
            return False, None

        row, col = pos
        square = self.board[row][col]
        if square == EMPTY:
            return True, 0
        elif square == BIG_DOT:
            return True, 10
        elif isinstance(square, Player):
            # Can't kill each other if both superspeed
            if player.superspeed_ticks > 0 and square.superspeed_ticks == 0:
                square.alive = False
                return True, 100

        return False, None

    def process_squares(self, old, new, player):
        if new == BIG_DOT:
            player.superspeed_ticks = 50

    def spawn_player(self, username):
        r, c = self.random_empty_location()
        new_player = Player(self, username, (r,c))
        self.leaderboard[username] = 0
        self.players[username] = new_player
        self.board[r][c] = new_player
        return new_player

    def change_player_direction(self, username, next_direction):
        self.players[username].change_direction(next_direction)

    def restart_player(self, player):
        old_r, old_c = player.position
        self.board[old_r][old_c] = EMPTY

        new_r, new_c = self.random_empty_location()
        self.board[new_r][new_c] = player
        player.position = new_r, new_c

        # Reset to zero
        self.leaderboard[player.username] = 0
        player.alive = True

    def move_player(self, player):
        if player.superspeed_ticks == 0 and self.num_ticks % 2 == 1:
            return

        row, col = player.position # most definitely bad design lol fix this later

        # If player can go in next_direction, take that direction. Otherwise, use old direction
        new_pos = direction_to_lambda[player.next_direction]((row, col))
        new_pos = self.wrap_pos(new_pos)
        movable, score = self.position_can_move_to(player, new_pos)
        if movable and player.direction != opposite_direction(player.next_direction):
            player.direction = player.next_direction
        else:
            new_pos = direction_to_lambda[player.direction]((row, col))
            new_pos = self.wrap_pos(new_pos)
            movable, score = self.position_can_move_to(player, new_pos)

        if movable:
            player.position = new_pos
            new_row, new_col = new_pos

            self.process_squares(self.board[row][col], self.board[new_row][new_col], player)
            self.board[row][col] = EMPTY
            self.board[new_row][new_col] = player
            self.leaderboard[player.username] += score

        if player.superspeed_ticks > 0:
            player.superspeed_ticks -= 1

    def remove_player(self, player):
        row, col = player.position
        self.board[row][col] = EMPTY
        del self.leaderboard[player.username]
        del self.players[player.username]

    def tick(self):
        for _, player in self.players.items():
            if player.alive:
                self.move_player(player)

        self.num_ticks += 1
        self.timestamp = time.time()


class Player:
    def __init__(self, game, username, pos):
        self.game = game
        self.username = username
        self.position = pos
        self.direction = 'd'
        self.next_direction = 'd'
        self.superspeed_ticks = 0
        self.alive = True

    def change_direction(self, next_direction):
        assert next_direction in direction_to_lambda, 'Invalid direction'
        self.next_direction = next_direction

    def __str__(self):
        return self.username[0]

    def __repr__(self):
        return self.username


