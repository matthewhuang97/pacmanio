import game
from struct import *
import pdb
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
    offset = calcsize('!II')
    pdb.set_trace()
    player_position = body[:offset]
    rest_of_body = body[offset:].decode('utf-8')
    username = rest_of_body[:MAX_LENGTH].strip()
    board = rest_of_body[MAX_LENGTH:]

    shared_data['username'] = username
    print(f'Player creation successful: {username}')
    print('You have joined the game. Move with the wasd keys.')

    print_client_board(board)


def move_success(body, shared_data):
    board = body.decode('utf-8')
    print_client_board(board)