from struct import pack
version = b'\x01'
import pdb

def create_success(conn, username, shared_data):
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

    # Should probably send the entire game... but it's a pain..
    game_state = shared_data['game']
    board = game_state.board

    print(board)
    packed_board = game_state.pack_board(username) # there's a bug where packed board isn't working on the second person idk why

    player_position = game_state.players[username].position
    encoded_position = pack('II', player_position[0], player_position[1])

    encoded_username = username.encode('utf-8')

    body = encoded_position + encoded_username + packed_board

    send_to_client(conn, b'\x02', body)

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

def move_success(conn, username, shared_data):
    g = shared_data['game']
    packed_game = g.pack_board(username)
    print('move success!')
    send_to_client(conn, b'\x03', packed_game)


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
    conn.send(header + body)