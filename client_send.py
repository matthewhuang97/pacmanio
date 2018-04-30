from struct import pack

version = b'\x01'

MAX_LENGTH = 5

def padded(string):
    len_to_pad = MAX_LENGTH - len(string)
    return string + ' ' * len_to_pad

def initialize_player(sock):
    username = input('Welcome to Pacman.io! Enter a username (max 5 chars)\n')
    send_to_server(b'\x01', padded(username).encode('utf-8'), sock)


def send_to_server(opcode, body, conn):
    """Sends a message to server.

    The message sent will have the following structure:
    - Header:
        - Version number (byte)
        - Length of payload (unsigned int)
        - Opcode (byte)
    - Body: optional payload

    Args:
        opcode: single byte representing function opcode
        body: body of the message to send, bytes object
        conn: connection object representing server to which to send
            request.

    """
    header = version + pack('!I', len(body)) + opcode
    message = header + body

    try:
        conn.send(message)
    except:
        # close the client if the connection is down
        print('ERROR: connection down')
        thread.exit()
        sys.exit()
    return