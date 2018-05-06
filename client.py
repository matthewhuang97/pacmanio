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

version = b'\x01'
recv_opcodes = {
    b'\x00': client_receive.general_failure,
    b'\x02': client_receive.create_success,
    b'\x03': client_receive.game_state,
    b'\x04': client_receive.restart_success,
}

SECS_PER_TICK = 0.1

# header protocol: See README for more details
#     version number (c)
#     body length (I)
#     opcode (c)
header_fmt = '!cIc'
header_len = calcsize(header_fmt)
shared_data = {'game_states':[]}

# Globals
move_counter = 0
game_states = []


def quit():
    os.system('stty echo')
    os.kill(os.getpid(), signal.SIGINT)

def simulate_step(client_game):
    client_game.tick()


def on_press(key):
    if key == Key.esc:
        print('Bye')
        quit()
    try:
        char = key.char
        if char == 'r':
            client_send.restart_player(shared_data['username'], sock)
    except:
        return

    # Emulate on client
    # shared_data['player'].change_direction(char)

    # Send move to server
    client_send.make_move(char, shared_data['username'], sock)


def listener():
    # Collect keypress events once the game begins
    with Listener(on_press=on_press) as listener:
        os.system('stty -echo')
        listener.join()

def run_screen(stdscr):
    shared_data['scr'] = stdscr
    # Receive + draw initial game state
    receive_message()
    # Clear screen
    stdscr.clear()
    client_update(stdscr, shared_data['game'])

def message_receiver():
    while True:
        receive_message()
        stdscr.refresh()

def client_update(stdscr, game):
    while True:
        time.sleep(SECS_PER_TICK)
        game.tick()
        stdscr.refresh()
        game.draw_screen(shared_data['scr'], shared_data['username'])

def enter_game():
    thread.start_new_thread(listener, ())
    curses.wrapper(run_screen)


def menu():
    while True:
        username = input('Welcome to Pacman.io! Enter a username (max 5 chars)\n')
        client_send.initialize_player(username[:5], sock)
        # If True, start game
        if receive_message():
            break
    enter_game()


def receive_message():
    try:
        msg = socket_util.recvall(sock, header_len)
    except:
        # close the client if the connection is down
        print('ERROR: connection down')
        quit()

    if len(msg) != 0:
        header = unpack(header_fmt, msg[:header_len])

        assert header[0] == version, f'Client v{version} incompatible with v{header[0]}'

        message_length = header[1]
        body_packed = socket_util.recvall(sock, message_length)

        assert header[1] == len(body_packed), 'Corrupted message'
        opcode = header[2]
        assert opcode in recv_opcodes, 'Unknown opcode'
    else:
        quit()

    return recv_opcodes[opcode](body_packed, shared_data)


def main():
    if os.geteuid() != 0 or len(sys.argv) != 3:
        print("Usage 'sudo python3 client.py <host> <port>'")
        sys.exit()

    host = sys.argv[1]
    port = sys.argv[2]
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Trying to connect ..')

    try:
        port = int(port)
        sock.connect((host, port))
    except:
        print(f'ERROR: Could not connect to {host}:{port}')
        sys.exit()

    print(f'Successfully connected to {host}:{port}!')
    menu()

if __name__ == '__main__':
    main()
