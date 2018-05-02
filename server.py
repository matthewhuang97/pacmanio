import sys
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

def game_handler(lock, game):
    while True:
        time.sleep(SECS_PER_TICK)
        with lock:
            game.tick()
            # game.print_board()

            # Broadcast game state to clients
            for conn in client_to_player:
                server_send.send_game(conn, game)

def disconnect(conn, lock, game):
    print('Disconnecting player...')
    with lock:
        game.remove_player(client_to_player[conn])
        del client_to_player[conn]
    thread.exit()

def client_handler(conn, lock, game):
    while True:
        try:
            msg = socket_util.recvall(sock, header_len)
        except:
            disconnect(conn, lock, game)

        if len(msg) == 0: # Disconnect signal
            print('WHOA')
            disconnect(conn, lock, game)

        header = unpack(header_fmt, msg[:header_len])

        if header[0] != version:
            thread.exit()

        body_packed = socket_util.recvall(sock, message_length)

        if header[1] == len(body_packed):
            thread.exit()

        opcode = header[2]
        with lock:
            opcode_to_function[opcode](conn, body_packed, game, client_to_player)


def main():
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

        lock = thread.allocate_lock()
        thread.start_new_thread(client_handler, (conn, lock, game))

if __name__ == '__main__':
    main()
