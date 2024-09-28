import asyncio
import websockets
import json
import time

from game import Player, bombs, explosions, players, lives, reset_game, map
from settings import SERVER_URL, SERVER_PORT

# Keep track of connected clients and assign player IDs
connected_clients = {}
game_is_running = False
start_time = 0
timestamp = 0

# Serialize the game state
def serialize_game_state():
    state = {
        'players': {p.player_id: [p.x,p.y] for p in players},
        'bombs': [
            {'x': b.x, 'y': b.y, 'player_id': b.player_id}
            for b in bombs
        ],
        'explosions': [
            {'sectors': e.sectors, 'bomb_type': e.bomb_type}
            for e in explosions
        ],
        'map': map.matrix,
        'lives': lives,
        'timestamp': timestamp
    }
    return state

# Process inputs received from clients
def process_input(player_id, input_data):
    controller = input_data.get('controller', {})
    player = next((p for p in players if p.player_id == player_id), None)
    if not player:
        return

    # Update player's movement
    player.move(controller)

    # Handle bomb placement
    if controller.get('place_bomb'):
        player.place_bomb()

async def handle_client(websocket):
    player_id = len(players)
    if player_id > 1:
        # Only two players are allowed
        await websocket.send(json.dumps({'error': 'Server full'}))
        await websocket.close()
        return

    # Add player to the game
    if player_id == 0:
        players.append(Player(1, 1, "BOMB_TYPE_1", player_id))
    else:
        players.append(Player(map.width - 2, map.height - 2, "BOMB_TYPE_2", player_id))

    connected_clients[player_id] = websocket

    try:
        while True:
            # Receive input from client
            message = await websocket.recv()
            input_data = json.loads(message)

            # Process input
            process_input(player_id, input_data)

    except websockets.exceptions.ConnectionClosed:
        print(f"Player {player_id + 1} disconnected")
        # Remove player from game
        players[:] = [p for p in players if p.player_id != player_id]
        lives[player_id] = 0
        del connected_clients[player_id]

async def game_loop():
    global start_time, game_is_running, timestamp
    while True:
        if len(players) == 2 and not game_is_running:
            start_time = time.time()
            game_is_running = True
        if game_is_running and len(players) == 2:
            timestamp = time.time() - start_time
        else:
            game_is_running = False

        # Update bombs and explosions
        for bomb in bombs:
            bomb.update()
        for explosion in explosions:
            explosion.update()

        # Send game state to all connected clients
        state = serialize_game_state()
        message = json.dumps(state)
        await asyncio.gather(*(client.send(message) for client in connected_clients.values()))

        await asyncio.sleep(1 / 60)  # Run at ~60 FPS

def main():
    reset_game()
    start_server = websockets.serve(handle_client, '0.0.0.0', SERVER_PORT)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.create_task(game_loop())
    print(f"Server started on ws://{SERVER_URL}:{SERVER_PORT}")
    loop.run_forever()

if __name__ == "__main__":
    main()
