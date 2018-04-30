import server_send
import game

def create_request(conn, body, shared_data):
    username = body.decode('utf-8').strip()

    if username in shared_data['game'].players.keys():
        # User already exists
        server_send.general_failure(conn, 'This user already exists')
    else:
        # Create new player
        shared_data['game'].spawn_player(username)
        print("New player successfully created")
        shared_data['game'].print_board()
        server_send.create_success(conn, username, shared_data)


def move_request(conn, body, shared_data):
    decoded_body = body.decode('utf-8')
    move = decoded_body[:1]
    username = decoded_body[1:]

    g = shared_data['game']
    player = g.players[username]

    g.update_state(player, move)

    server_send.move_success(conn, username, shared_data)






    print("move")