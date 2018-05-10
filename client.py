import os
import sys
import game
import socket, socket_util
import signal
import curses
import time
from struct import *
import _thread as thread
import client_receive, client_send
from pynput.keyboard import Key, Listener
from utils import debug

version = b'\x01'
recv_opcodes = {
    b'\x00': client_receive.general_failure,
    b'\x01': client_receive.create_success,
    b'\x02': client_receive.receive_game_state,
}

# Number of seconds corresponding to a game tick
SECS_PER_TICK = 0.1

# Header protocol:
#     version number (c)
#     body length (I)
#     opcode (c)
header_fmt = '!cIc'
header_len = calcsize(header_fmt)

shared_data = {}

def quit():
    """Exits client.
    """
    os.system('stty echo')
    os.kill(os.getpid(), signal.SIGINT)

def on_press(key):
    """Handles keypress events for pynput.keyboard.Listener.

    Args:
        key: key that was pressed.

    Side effects:
        If key is a valid move, sends to server and emulates it locally.
    """
    if key == Key.esc:
        quit()
    try:
        char = key.char
        if char == 'r':
            client_send.restart_player(shared_data['username'], shared_data['sock'])
            return
    # Exception occurs when key.char fails, meaning the key pressed was not a character
    except:
        return

    # If a valid key in the game
    next_direction = char
    if next_direction in ['w', 'a', 's', 'd']:
        game = shared_data['game']
        username = shared_data['username']

        # Emulate on client, and keep track of action + when it was done
        game.change_player_direction(username, next_direction)
        shared_data['log'].append((time.time(), next_direction))

        # Send to server
        client_send.make_move(char, shared_data['sock'])

def enter_game(stdscr):
    """Initializes game.

    Args:
        stdscr: The standard screen passed into the curses wrapper.

    Side effects:
        Stores the screen object in shared_data['scr']
        Stores the lock object in shared_data['game_lock']
        Simulates game and logs actions to shared_data['log']
        Starts a thread to receive client key presses.
        Starts a thread to receive server updates.
    """
    shared_data['scr'] = stdscr
    stdscr.clear()

    game_lock = thread.allocate_lock()
    shared_data['game_lock'] = game_lock

    # Wait for first game state to be received
    receive_message()

    # Start a thread to receive client key presses
    thread.start_new_thread(key_listener, ())
    # And a thread to receive server updates
    thread.start_new_thread(server_listener, ())

    # Loop to simulate the game on the client
    while True:
        time.sleep(SECS_PER_TICK)
        with game_lock:
            game = shared_data['game']
            game.tick()
            client_receive.debug(game.num_ticks)
            # Append 'tick' actions to log.
            shared_data['log'].append((time.time(), 'tick'))

            game.draw_screen(stdscr, shared_data['username'])
            stdscr.refresh()

def key_listener():
    """Collect keypress events once the game begins. 
    """
    with Listener(on_press=on_press) as listener:
        os.system('stty -echo')
        listener.join()

def server_listener():
    """Receives and processes server messages.
    """
    while True:
        receive_message()

def receive_message():
    """Receives and processes a single server message.

    Server socket should be stored in shared_data['sock']
    """
    try:
        msg = socket_util.recvall(shared_data['sock'], header_len)
    except:
        # Close the client if the connection is down
        quit()

    if len(msg) != 0:
        header = unpack(header_fmt, msg[:header_len])
        assert header[0] == version, f'Client v{version} incompatible with v{header[0]}'

        message_length = header[1]
        body_packed = socket_util.recvall(shared_data['sock'], message_length)

        assert header[1] == len(body_packed), 'Corrupted message'
        opcode = header[2]
        assert opcode in recv_opcodes, 'Unknown opcode'
    else:
        quit()

    return recv_opcodes[opcode](body_packed, shared_data)

def menu():
    """Display entry message and enters game when server confirms.
    """
    while True:
        username = input('Welcome to Pacman.io! Enter a username (max 5 chars)\n')
        client_send.initialize_player(username[:5], shared_data['sock'])
        # If True, start game
        if receive_message():
            break
    curses.wrapper(enter_game)

def main():
    if os.geteuid() != 0 or len(sys.argv) != 3:
        print("Usage 'sudo python3 client.py <host> <port>'")
        sys.exit()

    host = sys.argv[1]
    port = sys.argv[2]
    shared_data['sock'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    shared_data['log'] = []

    try:
        port = int(port)
        shared_data['sock'].connect((host, port))
    except:
        print(f'ERROR: Could not connect to {host}:{port}')
        sys.exit()

    print(f'Successfully connected to {host}:{port}!')
    menu()

if __name__ == '__main__':
    main()
