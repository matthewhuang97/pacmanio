import pdb
import game
from struct import *
import _thread as thread
import pickle
import pdb

def debug(txt):
    with open('/tmp/log.txt', 'a') as f:
        f.write(str(txt) + '\n')

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

def reconciliate(shared_data, server_game):
    """Reconciles the game state received from the server with the client.

    Args:
        shared_data: Dictionary of shared data between server and client. 
        server_game: Game state from server.

    Side effects:
        Resimulates actions taken locally since the synced time of the game state
        received from the server.
        Removes past data from log that has already been synced to the server.
    """
    with shared_data['game_lock']:
        server_time = server_game.timestamp
        log = shared_data['log']

        ind = 0
        for ind, (t, _) in enumerate(log):
            if t >= server_time:
                break
        log = log[ind:]
        shared_data['log'] = log

        for _, event in log:
            if event == 'tick':
                server_game.tick()
            else:
                next_direction = event
                server_game.change_player_direction(shared_data['username'], next_direction)
        shared_data['game'] = server_game

def receive_game_state(encoded_game, shared_data):
    """Called upon receiving a game state from the server.
    Args:
        shared_data: Dictionary of shared data between server and client. 
        encoded_game: Encoded version of game state from server.
    """
    game = pickle.loads(encoded_game)

    if 'game' not in shared_data: # First time game state has been received
        shared_data['game'] = game
        game.init_curses()
    else:
        reconciliate(shared_data, game)

    player = game.players[shared_data['username']]
    if not player.alive:
        lost_game(shared_data['scr'])

def lost_game(scr):
    """Called upon dying in the game.
    Args:
        scr: Screen on which to display goodbye message.
    """
    scr.addstr("\nYou have died. Goodbye. You can exit with ESC, or press r to resume.")
    scr.refresh()

def restart_success(body, shared_data):
    """Called upon dying in the game.
    Args:
        body: body of message, should be the encoded game state
        shared_data: Dictionary of shared data between server and client.
    """
    receive_game_state(body, shared_data)
