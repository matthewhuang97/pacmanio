from pynput.keyboard import Key, Listener
import os
import sys
import socket
from struct import *
import _thread as thread

def movement():
    print('movement')

def quit():
    os.system('stty echo')
    sys.exit()

def on_press(key):
    if key == Key.esc:
        quit()

    try:
        char = key.char
        if char == 'a':
            movement()
    except:
        pass

    try:
        print(sock)
        sock.send('asdf')
        # sock.send(pack('!s', key.char))
    except:
        print('ERROR: connection down')
        quit()

def main():
    if os.geteuid() != 0 or len(sys.argv) != 3:
        print("Usage 'sudo python3 client.py <host> <port>'")
        sys.exit()

    host = sys.argv[1]
    port = sys.argv[2]
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        port = int(port)
        sock.connect((host, port))
    except:
        print(f'ERROR: Could not connect to {host}:{port}')
        sys.exit()

    print(f'Successfully connected to {host}:{port}!')

    # thread.start_new_thread(im_handler, (im_sock,))

    # Collect events until released
    with Listener(on_press=on_press) as listener:
        print('listener init')
        os.system('stty -echo')
        listener.join()

    # while True:
        # cmd = get_input()
        # if process_input(cmd, sock, im_sock):
            # get_response(sock)

if __name__ == '__main__':
    main()
