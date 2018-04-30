import random
import curses
import copy
import pdb

UP = 'w'
DOWN = 's'
LEFT = 'a'
RIGHT = 'd'
class Game:
    def __init__(self, board):
        self.wall = 'O'
        self.empty = ' '
        self.player = 'X'
        self.num_rows = len(board)
        self.num_cols = len(board[0])
        self.board = board
        self.players = {}

    def pack_board(self, username):
        string_of_board = []

        def print_square(x):
            try:
                if x.username == username:
                    return 'X' # print an X for the current player
                else:
                    return str(x)
            except:
                return str(x)

        for row in self.board:
            str_of_row = [print_square(x) if x != '\n' else '' for x in row]
            string_row = ''.join(str_of_row)
            string_of_board.append(string_row)

        final_string = ','.join(string_of_board)
        return final_string.encode('utf-8')

    def print_board(self):
        for row in self.board:
            for sq in row:
                print(sq, end='')

    def random_empty_location(self):
        while True:
            r = random.randint(0, self.num_rows - 1)
            c = random.randint(0, self.num_cols - 1)
            if self.board[r][c] == self.empty:
                return (r, c)

    def spawn_player(self, username):
        r, c = self.random_empty_location()
        new_player = Player(username, (r,c))
        self.players[username] = new_player
        self.board[r][c] = new_player

    def start_game(self):
        self.spawn_player()
        self.print_board()

    def is_valid(self, player, move):
        row, col = player.next(move)

        # Check if out of bounds
        if (col >= self.num_cols or col < 0 or row >= self.num_rows or row < 0):
            return False

        # Check if wall
        if self.board[row][col] == 'O':
            return False

        return True


    def update_state(self, player, move):
        if self.is_valid(player, move):
            # update the game board
            prev_r, prev_c = player.position

            new_r, new_c = player.next(move)

            self.board[prev_r][prev_c] = self.empty
            self.board[new_r][new_c] = player

            # move the player's position 
            player.move(move)
        else:
            # probably raise a custom exception
            pass

class Player:
    def __init__(self, username, pos):
        self.username = username
        self.position = pos

    def set_position(self, pos):
        self.position = pos

    def next(self, direction):
        row, col = self.position # # most definitely bad design lol fix this later
        if direction == UP:
            next_square = (row - 1, col)
        elif direction == DOWN:
            next_square = (row + 1, col)
        elif direction == LEFT:
            next_square = (row, col - 1)
        elif direction == RIGHT:
            next_square = (row, col + 1)
        return next_square

    def move(self, direction):
        self.position = self.next(direction) # validation is done by the game idk if that's good


    def __str__(self):
        return self.username[0]


# def run_screen(stdscr):
#     # Clear screen
#     stdscr.clear()
#     # Proceed with your program
#     stdscr.refresh()
#     stdscr.getkey()
#     print("Running some program")

# def main():
#     curses.wrapper(run_screen)

def load_new_game():
    board = []
    with open('board.txt', 'r') as f:
        for line in f:
            board.append(list(line))
    game = Game(board)
    return game

def main():
    game = load_new_game()
    game.start_game()

if __name__ == '__main__':
    main()
