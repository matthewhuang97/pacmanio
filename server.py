import sys
import copy
import time
import socket, socket_util
from struct import *
from game import Game
import server_receive
import server_send
import _thread as thread

version = b'\x01'
header_fmt = '!cIc'
header_len = calcsize(header_fmt)
opcode_to_function = {
    b'\x01': server_receive.create_request,
    b'\x02': server_receive.move_request,
    b'\x03': server_receive.restart_request,
}

client_to_player = {}

SECS_PER_TICK = 0.1
# Number of seconds of lag to impose on all connections
SECS_DELAY = 1

def game_handler(lock, game):
    """Game loop. 

    Args: 
        lock: _thread.lock object
        game: game object 

    Waits SECS_PER_TICK in between advancing each game state.
    Imposes SECS_DELAY of artificial lag in sending to each client.
    """
    past_game_states = []
    while True:
        time.sleep(SECS_PER_TICK)
        with lock:
            game.tick()

            game_copy = copy.deepcopy(game)
            past_game_states.append(game_copy)
            # If true, we've queued states for SECS_DELAY and can begin sending the old states
            if len(past_game_states) > SECS_DELAY // SECS_PER_TICK:
                game_to_send = past_game_states[0]
                past_game_states = past_game_states[1:] # Remove sent game state from list of game states

                # Broadcast game state to clients
                for conn, player in client_to_player.items():
                    # Only send to the client if the player exists -- this matters when we impose
                    # our artificial lag (the server will send an old state in which the client does
                    # not yet exist, which will confuse the clients)
                    if player.username in game_to_send.players:
                        server_send.send_game(conn, game_to_send)

def disconnect(conn, lock, game):
    """Removes player from game and cleans up thread.

    Args:
        conn: socket of corersponding player
        lock: _thread.lock object for the game state
        game: game state to remove player from

    Side effects:
        Removes player from game and removes from client_to_player dictionary.
        Exits thread.
    """
    print('Disconnecting player...')
    with lock:
        game.remove_player(client_to_player[conn])
        del client_to_player[conn]
    thread.exit()

def client_handler(conn, lock, game):
    """Handles requests sent from the client to the server.

    Args:
        conn: connection on which to listen for messages.
        lock: lock object
        game: game the client is in.
    """
    while True:
        try:
            msg = socket_util.recvall(conn, header_len)
        except:
            disconnect(conn, lock, game)

        header = unpack(header_fmt, msg[:header_len])

        if header[0] != version: # Check header version.
            thread.exit()

        # header[1] is message length
        body_packed = socket_util.recvall(conn, header[1])
        if header[1] != len(body_packed):
            thread.exit()

        opcode = header[2]
        with lock:
            opcode_to_function[opcode](conn, body_packed, game, client_to_player)

def main():
    """Initializes game, starts a thread to handle it, and binds a socket to listen.
    """
    if(len(sys.argv) != 3):
        print("Usage 'python server.py <host> <port>'. Example: python server.py 10.252.215.26 8090")
        sys.exit()

    game = Game()
    lock = thread.allocate_lock()
    thread.start_new_thread(game_handler, (lock, game))

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    host = str(sys.argv[1])
    port = int(sys.argv[2])
    sock.bind((host, port))
    sock.listen(5)

    print(f'Listening for connections on {host}:{port}...')
    while True:
        conn, addr = sock.accept()
        print(f'Picked up new client {addr}')

        thread.start_new_thread(client_handler, (conn, lock, game))

if __name__ == '__main__':
    main()
