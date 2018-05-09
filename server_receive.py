import random
import server_send
import pdb

def create_request(conn, body, game, client_to_player):
    username = body.decode('utf-8').strip()

    if username in game.players:
        server_send.general_failure(conn, 'This user already exists')
        return

    # Create new player
    player = game.spawn_player(username)
    client_to_player[conn] = player
    server_send.create_success(conn, username, game)
    print('New player successfully created')

def restart_request(conn, body, game, client_to_player):
    # Use username to double-check
    username = body.decode('utf-8')
    player = client_to_player[conn]
    assert player.username == username
    game.restart_player(player)

# Rate at which move requests are dropped
REQUEST_DROP_RATE = 0.0
def move_request(conn, body, game, client_to_player):
    if random.random() < REQUEST_DROP_RATE:
        return
    move = body.decode('utf-8')
    player = client_to_player[conn]
    player.change_direction(move)
