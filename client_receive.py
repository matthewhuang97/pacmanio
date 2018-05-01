import pdb
import game
from struct import *
import _thread as thread
import pickle

MAX_LENGTH = 5

def print_client_board(packed_board):
    board = packed_board.split(',')
    for row in board:
        print(row)

def general_failure(body, shared_data):
    """Handles failure messsages from the server.

    Args:
        body: bytes received from server. Represents the error message
            that is the utf-8 encoding of a string.
        shared_data: Dictionary of shared data between server and client.

    Side effects:
        Prints error message received from server.
    """
    print("ERROR: " + body.decode("utf-8"))

def create_success(body, shared_data):
    """Handles create account success message from the server.

    Args:
        body: bytes received from server. Body should be the UTF-8 encoding of the
            account id of the user whose account was just made.
        shared_data: Dictionary of shared data between server and client.

    Side effects:
        Prints message notifying user of successful account creation.
        Logs into the account of the user who was just created.
        Updates dictionary of shared data so the client knows which user it is.
    """

    username = body.decode('utf-8').strip()
    shared_data['username'] = username
    print(f'Player creation successful: {username}')
    print('You have joined the game. Move with the wasd keys.')

    return True

def game_state(encoded_game, shared_data):
    game = pickle.loads(encoded_game)
    game.draw_board(shared_data['scr'])

    # TODO: get rid of this gross thing
    for player in game.leaderboard:
        if player.username == shared_data['username'] and not player.alive:
            lost_game('', shared_data)

def lost_game(body, shared_data):
    scr = shared_data['scr']
    scr.addstr("\nYou have died. Goodbye. You can exit with CTRL + C, or press r to resume.")
    scr.refresh()

def restart_success(body, shared_data):
    game_state(body, shared_data)




