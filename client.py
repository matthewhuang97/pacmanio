from pynput.keyboard import Key, Listener
import os
import sys
import socket
from struct import *
import _thread as thread
import client_receive, client_send

version = b'\x01'
valid_keys = ['w', 'a', 's', 'd']

opcodes = {
    b'\x00': client_receive.general_failure,
    # b'\x01': client_receive.login_success,
    b'\x02': client_receive.create_success,
    b'\x03': client_receive.move_success,
    # b'\x04': client_receive.send_message_success,
    # b'\x05': client_receive.get_messages_success,
    # b'\x06': client_receive.delete_success,
    # b'\x07': client_receive.logout_success,
}
# header protocol: See README for more details
#     version number (c)
#     body length (I)
#     opcode (c)
header_fmt = '!cIc'
header_len = calcsize(header_fmt)

shared_data = {}

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
        if char in valid_keys:
            movement()
            try:
                # Send message 
                message = char + shared_data['username']
                client_send.send_to_server(b'\x02', message.encode('utf-8'), sock)
            except:
                print('ERROR: connection down')
                quit()
    except:
        pass

def handler(sock):
    """Waits for server responses and handles it if it gets one.

    Args:
        sock: The socket object on which to wait for a message.

    Side effects:
        The appropriate function to handle the message is called.
    """
    while True:
        try:
            msg = sock.recv(1024)
        except:
            # close the client if the connection is down
            print('ERROR: connection down')
            sys.exit()

        if len(msg) != 0:
            header = unpack(header_fmt, msg[:header_len])
            body_packed = msg[header_len:]

            assert header[0] == version, f'Client v{version} incompatible with v{header[0]}'
            assert header[1] == len(msg) - header_len, 'Corrupted message'
            opcode = header[2]
            assert opcode in opcodes, 'Unknown opcode'

            # send packet to correct handler
            opcodes[opcode](body_packed, shared_data)


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

    player_username = client_send.initialize_player(sock)
    thread.start_new_thread(handler, (sock,))

    # Collect keypress events once the game begins
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
