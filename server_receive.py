import server_send

def create_request(conn, body, game, client_to_player):
    username = body.decode('utf-8').strip()

    for player in game.leaderboard:
        # User already exists
        if username == player.username:
            server_send.general_failure(conn, 'This user already exists')
            return

    # Create new player
    player = game.spawn_player(username)
    client_to_player[conn] = player
    server_send.create_success(conn, username, game)
    print('New player successfully created')


def move_request(conn, body, game, client_to_player):
    decoded_body = body.decode('utf-8')
    move = decoded_body[0]

    player = client_to_player[conn]
    player.change_direction(move)
