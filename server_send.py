from struct import pack
import pdb
import pickle

version = b'\x01'

def create_success(conn, username, game_state):
    """Send message of successful account creation to client.

    Args:
        conn: Socket, socket to which to send the message.
        username: Body should be a UTF-8 encoding of the account name
            that was just created (max 5 chars)

    Side effects:
        Sends a message to the connection socket using the
        create_success opcode. The body of the message is the packed version
        (string) of the account username (unsigned int) that has been created.
    """

    send_to_client(conn, b'\x02', username.encode('utf-8'))

def restart_success(conn, game):
    send_to_client(conn, b'\x04', pickle.dumps(game))

def send_game(conn, game):
    send_to_client(conn, b'\x03', pickle.dumps(game))

def general_failure(conn, err_msg):
    """Handle a general failure and send message to client.

    Args:
        conn: Socket, socket to which to send the message.
        err_msg: String, describing the error that occured.

    Side effects:
        Sends a message to the connection socket using the
        general_failure opcode. The body of the message is a UTF-8
        encoding of the error message.
    """
    err_send = err_msg.encode('utf-8')
    send_to_client(conn, b'\x00', err_send)


def send_to_client(conn, opcode, body):
    """Send encoded message to a connection.

    Args:
        conn: Socket, socket to which to send the message.
        opcode: Opcode of function for client to call.
        body: Additional body of message, if any.

    Side effects:
        Sends a message to the connection socket using the
        given opcode and body of message. The message is setup as:
        - header: Includes version number (byte), length of additional
            message body (unsigned int packed as !I), and opcode (byte)
        - body: body of message
    """
    header = version + pack('!I', len(body)) + opcode
    try:
        conn.sendall(header + body)
    except:
        pass
