import pygame
import time
import sys
import asyncio
import json

from settings import *

async def main():
    # Initialize Pygame
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Overblocked")

    # Connect to server
    uri = "ws://10.9.11.137:8765"
    #uri = "ws://54.91.210.37:8765"
    # uri = "ws://10.9.11.137:3306"
    try:
        websocket = await asyncio.wait_for(websockets.connect(uri), timeout=5)
    except Exception as e:
        print(f"Unable to connect to server: {e}")
        pygame.quit()
        return

    # Create clock object to manage frame rate
    clock = pygame.time.Clock()

    # Variables to store game state
    game_state = None

    # Main loop
    running = True
    while running:
        dt = clock.tick(60)  # Delta time in milliseconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get key presses
        keys = pygame.key.get_pressed()
        controller_input = {
            'up': keys[pygame.K_UP] or keys[pygame.K_w],
            'down': keys[pygame.K_DOWN] or keys[pygame.K_s],
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
            'place_bomb': keys[pygame.K_SPACE]
        }

        # Send input to server
        input_data = {'controller': controller_input}
        await websocket.send(json.dumps(input_data))

        # Receive game state from server
        try:
            message = await websocket.recv()
            game_state = json.loads(message)
        except websockets.exceptions.ConnectionClosed:
            print("Server connection closed")
            running = False
            break

        # Clear the screen and redraw the grid and HUD
        screen.fill(BACKGROUND_COLOR)
        if game_state:
            draw_game(screen, game_state)
            print(game_state)
            draw_hud(screen, game_state['timestamp'], game_state['lives'])

        # Update display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()

def draw_game(screen, game_state):
    # Draw the map
    map_matrix = game_state['map']
    for row in range(len(map_matrix)):
        for col in range(len(map_matrix[0])):
            cell_value = map_matrix[row][col]
            color = BACKGROUND_COLOR
            if cell_value == 1:
                color = OBSTACLE_COLOR  # Unbreakable
            elif cell_value == 2:
                color = BREAKABLE_COLOR  # Breakable
            elif cell_value == -2:
                color = BREAKING_COLOR  # Breaking
            elif cell_value == 3:
                color = BOMB_COLOR  # Bomb
            pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, GRID_COLOR, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE), 1)

    # Draw bombs
    for bomb in game_state['bombs']:
        x = bomb['x']
        y = bomb['y']
        pixel_x = x * TILE_SIZE
        pixel_y = y * TILE_SIZE + HUD_HEIGHT
        pygame.draw.rect(screen, BOMB_COLOR, (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))

    # Draw explosions
    for explosion in game_state['explosions']:
        bomb_type = explosion['bomb_type']
        if bomb_type == 'BOMB_TYPE_1':
            color = PLAYER1_EXPLOSION_COLOR
        elif bomb_type == 'BOMB_TYPE_2':
            color = PLAYER2_EXPLOSION_COLOR
        else:
            color = (255, 0, 0)  # Default color if bomb_type is unknown
        for sector in explosion['sectors']:
            x, y = sector
            pixel_x = x * TILE_SIZE
            pixel_y = y * TILE_SIZE + HUD_HEIGHT
            pygame.draw.rect(screen, color, (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))

    # Draw players
    # Load the sprite sheet
    player1_idle_sprite = pygame.image.load('assets/caco-idle.png').convert_alpha()
    player1_idle_sprite = pygame.image.load('assets/caco-idle.png').convert_alpha()

    if player1_idle_sprite is None:
        print("Image failed to load.")
    else:
        print("Image loaded successfully.")
        print(player1_idle_sprite.get_size())
        # Get original sprite dimensions
        original_width, original_height = player1_idle_sprite.get_size()

        # Calculate aspect ratio and new dimensions keeping within TILE_SIZE
        aspect_ratio = original_width / original_height

        # Calculate the new width and height while keeping the aspect ratio
        if aspect_ratio > 1:  # Image is wider than tall
            new_width = TILE_SIZE
            new_height = int(TILE_SIZE / aspect_ratio)
        else:  # Image is taller than wide
            new_height = TILE_SIZE
            new_width = int(TILE_SIZE * aspect_ratio)

        # Resize the sprite while maintaining the aspect ratio
        player1_idle_sprite = pygame.transform.scale(player1_idle_sprite, (new_width, new_height))
    for player in game_state['players']:
        x = player['x']
        y = player['y']
        pixel_x = x * TILE_SIZE  # Calculate pixel_x here
        pixel_y = y * TILE_SIZE + HUD_HEIGHT  # Calculate pixel_y here
        
        # Check if it's player 1 and draw the sprite
        if player['id'] == 0:
            screen.blit(player1_idle_sprite, (pixel_x, pixel_y))  # Use the player sprite at the calculated pixel coordinates
        else:
            # Draw other players as rectangles for now
            color = PLAYER_2_COLOR
            pygame.draw.rect(screen, color, (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))
# Function to draw the HUD
def draw_hud(screen, timer, lives):
    # Create a black background for the HUD
    pygame.draw.rect(screen, HUD_COLOR, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
    font = pygame.font.SysFont(None, 36)
    # Player 1's lives (left corner)
    text_p1 = font.render(f"P1 Lives: {lives[0]}", True, (255, 255, 255))
    screen.blit(text_p1, (10, 10))
    # Player 2's lives (right corner)
    text_p2 = font.render(f"P2 Lives: {lives[1]}", True, (255, 255, 255))
    screen.blit(text_p2, (SCREEN_WIDTH - 150, 10))
    # Timer in the middle
    text_timer = font.render(f"Timer: {int(timer)}", True, (255, 255, 255))
    screen.blit(text_timer, (SCREEN_WIDTH // 2 - 50, 10))

if __name__ == '__main__':
    import websockets
    asyncio.run(main())
