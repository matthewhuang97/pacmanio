from struct import pack

version = b'\x01'

MAX_LENGTH = 5

def padded(string):
    """Pads a string with whitespace to be MAX_LENGTH characters.

    Args:
        string: string to pad, should be at most MAX_LENGTH characters.

    Returns:
        string, exactly MAX_LENGTH long.
    """
    len_to_pad = MAX_LENGTH - len(string)
    return string + ' ' * len_to_pad

def initialize_player(username, conn):
    """Send a request to the server to initialize a player.

    Args:
        username: string, representing username of the new player.
            Should be at most MAX_LEN characters.
        conn: connection object representing server to which to send
            request.
    """
    send_to_server(b'\x01', padded(username).encode('utf-8'), conn)

def make_move(move_char, username, conn):
    """Send a request to the server to change a player's direction.

    Args:
        conn: connection object representing server to which to send
            request.
    """
    send_to_server(b'\x02', move_char.encode('utf-8'), conn)

def restart_player(conn):
    """Send a request to the server to restart a player.

    Args:
        conn: connection object representing server to which to send
            request.
    """
    send_to_server(b'\x03', conn)

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
        conn.sendall(msg)
    except:
        # close the client if the connection is down
        print('ERROR: connection down')
        os.system('stty echo')
        os.kill(os.getpid(), signal.SIGINT)
