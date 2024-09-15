import asyncio
import websockets
import json
import time

from game import GameController, GameMap, Player, bombs, explosions, players, placed_bombs, lives, reset_game, map
from settings import PLAYER_LIVES

# Keep track of connected clients and assign player IDs
connected_clients = {}
next_player_id = 0

# Serialize the game state
def serialize_game_state():
    state = {
        'players': [
            {'id': p.player_id, 'x': p.x, 'y': p.y}
            for p in players
        ],
        'bombs': [
            {'x': b.x, 'y': b.y, 'player_id': b.player_id}
            for b in bombs
        ],
        'explosions': [
            {'sectors': e.sectors}
            for e in explosions
        ],
        'map': map.matrix,
        'lives': lives,
        'timestamp': time.time()
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

async def handle_client(websocket, path):
    global next_player_id

    # Assign player ID
    player_id = next_player_id
    next_player_id += 1

    if player_id > 1:
        # Only two players are allowed
        await websocket.send(json.dumps({'error': 'Server full'}))
        await websocket.close()
        return

    # Add player to the game
    if player_id == 0:
        players.append(Player(1, 1, "green", player_id))
    else:
        players.append(Player(map.width - 2, map.height - 2, "yellow", player_id))

    lives.append(PLAYER_LIVES)
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
    while True:
        # Update bombs and explosions
        for bomb in bombs[:]:
            bomb.update()
        for explosion in explosions[:]:
            explosion.update()

        # Send game state to all connected clients
        state = serialize_game_state()
        message = json.dumps(state)
        await asyncio.gather(*(client.send(message) for client in connected_clients.values()))

        await asyncio.sleep(1 / 60)  # Run at ~60 FPS

def main():
    reset_game()
    start_server = websockets.serve(handle_client, 'localhost', 8765)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.create_task(game_loop())
    print("Server started on ws://localhost:8765")
    loop.run_forever()

if __name__ == "__main__":
    main()
