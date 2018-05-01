from struct import pack

version = b'\x01'
valid_keys = ['w', 'a', 's', 'd']

MAX_LENGTH = 5

def padded(string):
    len_to_pad = MAX_LENGTH - len(string)
    return string + ' ' * len_to_pad

def initialize_player(username, conn):
    send_to_server(b'\x01', padded(username).encode('utf-8'), conn)

def make_move(move_char, username, conn):
    if move_char in valid_keys:
        msg = move_char
        send_to_server(b'\x02', msg.encode('utf-8'), conn)

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
    msg = header + body

    try:
        conn.send(msg)
    except:
        # close the client if the connection is down
        print('ERROR: connection down')
        os.system('stty echo')
        os.kill(os.getpid(), signal.SIGINT)
