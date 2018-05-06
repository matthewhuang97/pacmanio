import pdb
import game
from struct import *
import _thread as thread
import pickle
import pdb

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

def apply_moves(game_state, move_list, last_processed_id):
    for action_id, function, args in move_list:
        if action_id > last_processed_id:
            if args:
                function(args)
            else:
                game_state.tick()

def reconciliate(shared_data, most_recent_server_state):
    shared_data['scr'].addstr('reconciliating')
    player = shared_data['player']

    # Find the actions requested by this player, processed by the server
    if player.username not in most_recent_server_state.moves:
        # print(player.username, most_recent_server_state.moves.keys())
        # shared_data['scr'].addstr(str(most_recent_server_state.moves.keys()))
        # shared_data['scr'].addstr('player not found')
        last_client_game_state = most_recent_server_state
        apply_moves(last_client_game_state, shared_data['actions'], 0)
        return

    if most_recent_server_state.moves[player] == []:
        shared_data['scr'].addstr('at most recent server time, player did not make changes')

    # If no actions processed by server, we're done
        #most_recent_server_state.draw_screen(shared_data['scr'], shared_data['username'])
        #shared_data['scr'].refresh()
        last_client_game_state = most_recent_server_state
        apply_moves(last_client_game_state, shared_data['actions'], 0)
        return

    shared_data['scr'].addstr('made it')

    # Get the most recent one
    time_of_last_action_processed = actions_processed.pop()

    # Apply all the moves that have happened since
    apply_moves(last_synced_game_state, shared_data['actions'], time_of_last_action_processed)
    last_synced_game_state.draw_screen(shared_data['scr'], shared_data['username'])
    shared_data['scr'] = last_synced_game_state


def game_state(encoded_game, shared_data):
    game = pickle.loads(encoded_game)

    if 'game_initialized' not in shared_data:
        print('first time')
        shared_data['game_initialized'] = True
        game.init_curses()
        shared_data['game'] = game
        game.draw_screen(shared_data['scr'], shared_data['username'])

        # sorry another gross thing
        for player in game.leaderboard:
            if player.username == shared_data['username']:
                shared_data['player'] = player
                break
    else:
        reconciliate(shared_data, game)


    # TODO: get rid of this gross thing
    for player in game.leaderboard:
        if player.username == shared_data['username'] and not player.alive:
            lost_game('', shared_data)

def lost_game(body, shared_data):
    scr = shared_data['scr']
    scr.addstr("\nYou have died. Goodbye. You can exit with ESC, or press r to resume.")
    scr.refresh()

def restart_success(body, shared_data):
    game_state(body, shared_data)
