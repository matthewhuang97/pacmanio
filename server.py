import socket
import sys
import _thread as thread
from struct import *
import game
import server_receive


version = b'\x01'

header_fmt = '!cIc'
header_len = calcsize(header_fmt)

opcode_to_function = {
    b'\x01': server_receive.create_request,
    b'\x02': server_receive.move_request,
    # b'\x03': server_receive.list_accounts_request,
    # b'\x04': server_receive.send_message_request,
    # b'\x05': server_receive.get_messages_request,
    # b'\x06': server_receive.delete_request,
    # b'\x07': server_receive.logout_request,
}

def handler(conn, lock, shared_data):
    while True:
        try:
            print('trying to recv...')
            msg = conn.recv(1024)
        except:
            print('exception')
            sys.exit()
            thread.exit()

        print('received', msg)
        print('game state', shared_data['game'])

        if len(msg) == 0: # Disconnect signal
            thread.exit()

        header = unpack(header_fmt, msg[:header_len])
        body_packed = msg[header_len:]

        # Check that versions match up and check integrity of message
        # If not, drop the connection because there's nothing better to do.
        if header[0] != version or header[1] != len(msg) - header_len: 
            thread.exit()

        opcode = header[2]
        with lock:
            opcode_to_function[opcode](conn, body_packed, shared_data)


def main():
    if(len(sys.argv) != 3):
        print("Usage 'python server.py <host> <port>'. Example: python server.py 10.252.215.26 8090")
        sys.exit()

    shared_data = {'game':game.load_new_game()}
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    host = str(sys.argv[1])
    port = int(sys.argv[2])
    sock.bind((host, port))
    sock.listen(5)

    print(f'Listening for connections on {host}:{port}...')
    while True:
        conn, addr = sock.accept()
        print(f'Picked up new client {addr}')

        lock = thread.allocate_lock()
        thread.start_new_thread(handler, (conn, lock, shared_data))

if __name__ == '__main__':
    main()
