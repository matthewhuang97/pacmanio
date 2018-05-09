import pdb
import game
from struct import *
import _thread as thread
import pickle
import pdb
from utils import debug

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
    return True

# Receives previous server game state and reconciles with actions in between to extrapolate to
# a new client state
def reconciliate(shared_data, server_game):
    with shared_data['game_lock']:
        server_time = server_game.timestamp
        log = shared_data['log']

        ind = 0
        for ind, (t, _) in enumerate(log):
            if t >= server_time:
                break
        log = log[ind:]

        # Replay events from log
        for _, event in log:
            if event == 'tick':
                server_game.tick()
            else:
                next_direction = event
                server_game.change_player_direction(shared_data['username'], next_direction)

        shared_data['game'] = server_game
        shared_data['log'] = log

def game_state(encoded_game, shared_data):
    game = pickle.loads(encoded_game)

    if 'game' not in shared_data:
        shared_data['game'] = game
        game.init_curses()
    else:
        reconciliate(shared_data, game)

    player = game.players[shared_data['username']]
    if not player.alive:
        lost_game(shared_data['scr'])

def lost_game(scr):
    scr.addstr("\nYou have died. Goodbye. You can exit with ESC, or press r to resume.")
    scr.refresh()
