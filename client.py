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
    uri = f"ws://{SERVER_URL}:{SERVER_PORT}"
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
    
    player1_idle_sprite = pygame.image.load('assets/caco-idle.png').convert_alpha()
    player2_idle_sprite = pygame.image.load('assets/cobra-idle.png').convert_alpha()
    trunk_sprite = pygame.image.load('assets/trunk.png').convert_alpha()
    rock_sprite = pygame.image.load('assets/rock.png').convert_alpha()
    mango_bomb_sprite = pygame.image.load('assets/mango-bomb.png').convert_alpha()
    venom_bomb_sprite = pygame.image.load('assets/venom-bomb.png').convert_alpha()
    # Draw the map
    map_matrix = game_state['map']
    for row in range(len(map_matrix)):
        for col in range(len(map_matrix[0])):
            cell_value = map_matrix[row][col]
            color = BACKGROUND_COLOR
            if cell_value == 1:
                screen.blit(rock_sprite, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT))
                color = OBSTACLE_COLOR  # Unbreakable
            elif cell_value == 2:
                screen.blit(trunk_sprite, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT))
                color = BREAKABLE_COLOR  # Breakable
            elif cell_value == -2:
                color = BREAKING_COLOR  # Breaking
            elif cell_value == 3:
                #screen.blit(mango_bomb_sprite, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT))
                color = BOMB_COLOR  # Bomb
            if cell_value != 2 and cell_value != 1 and cell_value != 3:
                pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE))
            #pygame.draw.rect(screen, GRID_COLOR, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE), 1)

    # Draw bombs
    for bomb in game_state['bombs']:
        x = bomb['x']
        y = bomb['y']
        pixel_x = x * TILE_SIZE
        pixel_y = y * TILE_SIZE + HUD_HEIGHT
        if bomb['player_id'] == 0:
            screen.blit(mango_bomb_sprite, (pixel_x, pixel_y))
        elif bomb['player_id'] == 1:
            screen.blit(venom_bomb_sprite, (pixel_x, pixel_y))

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
    
    
    #Não precisa mais fazer o resize, os sprites já estão no tamanho certo
    #if player1_idle_sprite is None:
    #    print("Image failed to load.")
    #else:
    #    print("Image loaded successfully.")
    #    print(player1_idle_sprite.get_size())
    #    # Get original sprite dimensions
    #    original_width, original_height = player1_idle_sprite.get_size()
#
    #    # Calculate aspect ratio and new dimensions keeping within TILE_SIZE
    #    aspect_ratio = original_width / original_height
#
    #    # Calculate the new width and height while keeping the aspect ratio
    #    if aspect_ratio > 1:  # Image is wider than tall
    #        new_width = TILE_SIZE
    #        new_height = int(TILE_SIZE / aspect_ratio)
    #    else:  # Image is taller than wide
    #        new_height = TILE_SIZE
    #        new_width = int(TILE_SIZE * aspect_ratio)
#
    #    # Resize the sprite while maintaining the aspect ratio
    #    player1_idle_sprite = pygame.transform.scale(player1_idle_sprite, (new_width, new_height))
#
    #    player2_idle_sprite = pygame.image.load('assets/cobra-idle.png').convert_alpha()
#
    #    if player2_idle_sprite is None:
    #        print("Image failed to load.")
    #    else:
    #        print("Image loaded successfully.")
    #        print(player2_idle_sprite.get_size())
    #        # Get original sprite dimensions
    #        original_width, original_height = player2_idle_sprite.get_size()
#
    #        # Calculate aspect ratio and new dimensions keeping within TILE_SIZE
    #        aspect_ratio = original_width / original_height
#
    #        # Calculate the new width and height while keeping the aspect ratio
    #        if aspect_ratio > 1:  # Image is wider than tall
    #            new_width = TILE_SIZE
    #            new_height = int(TILE_SIZE / aspect_ratio)
    #        else:  # Image is taller than wide
    #            new_height = TILE_SIZE
    #            new_width = int(TILE_SIZE * aspect_ratio)
    #        # Resize the sprite while maintaining the aspect ratio
    #        player2_idle_sprite = pygame.transform.scale(player2_idle_sprite, (new_width, new_height))
    
    for player in game_state['players']:
        x = player['x']
        y = player['y']
        pixel_x = x * TILE_SIZE  # Calculate pixel_x here
        pixel_y = y * TILE_SIZE + HUD_HEIGHT  # Calculate pixel_y here
        
        # Check if it's player 1 and draw the sprite
        if player['id'] == 0:
            sprite_width, sprite_height = 61, 80  # Tamanho do sprite (61x80)
            centralized_x = pixel_x + (TILE_SIZE - sprite_width) // 2
            centralized_y = pixel_y  # A altura já é a mesma, então não precisa ajustar
            screen.blit(player1_idle_sprite, (centralized_x, centralized_y))  # Use the player sprite at the calculated pixel coordinates
        else:
            sprite_width, sprite_height = 75, 80  # Tamanho do sprite (61x80)
            centralized_x = pixel_x + (TILE_SIZE - sprite_width) // 2
            centralized_y = pixel_y  # A altura já é a mesma, então não precisa ajustar
            screen.blit(player2_idle_sprite, (centralized_x, centralized_y))  # Use the player sprite at the calculated pixel coordinates
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

def load_player1_animation_frames():
    animations = {
        'down': [pygame.image.load(f'assets/caco-walking-down-frame-{i}.png').convert_alpha() for i in range(1, 9)],
        'up': [pygame.image.load(f'assets/caco-walking-up-frame-{i}.png').convert_alpha() for i in range(1, 9)],
        'left': [pygame.image.load(f'assets/caco-walking-left-frame-{i}.png').convert_alpha() for i in range(1, 9)],
        'right': [pygame.image.load(f'assets/caco-walking-right-frame-{i}.png').convert_alpha() for i in range(1, 9)],
    }
    return animations

if __name__ == '__main__':
    import websockets
    asyncio.run(main())
