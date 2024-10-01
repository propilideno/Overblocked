import pygame
import time
import sys
import asyncio
import json
import copy

from settings import *

async def main():
    # Initialize Pygame
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Overblocked")


    # Background image
    mapa_1 = pygame.image.load('./assets/maps/mapa_neve_com_pedra.png').convert()
    mapa_1 = pygame.transform.scale(mapa_1, (SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT))

    mapa_2 = pygame.image.load('./assets/maps/mapa_verde_com_pedra.png').convert()
    mapa_2 = pygame.transform.scale(mapa_2, (SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT))

    mapa_3 = pygame.image.load('./assets/maps/mapa_areia_com_pedra.png').convert()
    mapa_3 = pygame.transform.scale(mapa_3, (SCREEN_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT))

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
    game_state = [None, None]  # [Current State, Previous State]

    # Main loop
    running = True

    # Loading sprites
    global player1_animations, player2_animations, player1_idle_sprite, player2_idle_sprite, trunk_sprite, rock_sprite, mango_bomb_sprite, venom_bomb_sprite

    player1_animations = load_player1_animation_frames()
    player2_animations = load_player2_animation_frames()
    player1_idle_sprite = pygame.image.load(
        'assets/caco-idle.png').convert_alpha()
    player2_idle_sprite = pygame.image.load(
        'assets/cobra-idle.png').convert_alpha()
    trunk_sprite = pygame.image.load('assets/trunk.png').convert_alpha()
    rock_sprite = pygame.image.load('assets/rock.png').convert_alpha()
    mango_bomb_sprite = pygame.image.load(
        'assets/mango-bomb.png').convert_alpha()
    mango_bomb_sprite = pygame.transform.scale(mango_bomb_sprite, (65, 65))
    venom_bomb_sprite = pygame.image.load(
        'assets/venom-bomb.png').convert_alpha()
    venom_bomb_sprite = pygame.transform.scale(venom_bomb_sprite, (65, 65))

    animation_state = {
        '0': {
            'direction': 'down',
            'frame': 0,
            'last_update': time.time(),
            'is_moving': False
        },
        '1': {
            'direction': 'down',
            'frame': 0,
            'last_update': time.time(),
            'is_moving': False
        }
    }

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
            if game_state[0]:
                game_state[1] = copy.deepcopy(game_state[0])
            game_state[0] = json.loads(message)

        except websockets.exceptions.ConnectionClosed:
            print("Server connection closed")
            running = False
            break

        # Clear the screen and redraw the grid and HUD
        match sum(game_state[0]['lives'])%3:
            case 0:
                background_image = mapa_1
            case 1:
                background_image = mapa_2
            case 2:
                background_image = mapa_3
            case _:
                background_image = mapa_1
        screen.blit(background_image, (0, HUD_HEIGHT))

        if game_state[0]:
            if game_state[1]:
                update_animation_state(game_state[0]['players'], game_state[1]['players'], animation_state)
                print('==   Game State   ==')
                print(game_state[0])
                print('== Animation State ==')
                print(animation_state)
            else:
                # No previous state, set is_moving to False
                for id in animation_state:
                    animation_state[id]['is_moving'] = False

            draw_game(screen, game_state[0], animation_state)
            draw_hud(screen, game_state[0]['timestamp'], game_state[0]['lives'])

        # Update display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()


def update_animation_state(players_current_state: dict, players_last_state: dict, animation_state: dict) -> None:
    """
    in: (
            {"0": [3.0, 2.0], "1": [12.0, 9.0]},
            {"0": [2.9, 2.0], "1": [12.1, 9.0]}
        )
    """
    if players_current_state.keys() == players_last_state.keys():
        for id in players_current_state:
            dx = players_current_state[id][0] - players_last_state[id][0]
            dy = players_current_state[id][1] - players_last_state[id][1]
            animation_state[id]['is_moving'] = dx != 0 or dy != 0
            if (dx < 0 and dy < 0) or (dy < 0 and dx == 0):
                animation_state[id]['direction'] = 'up'
            elif (dx > 0 and dy > 0) or (dy > 0 and dx == 0):
                animation_state[id]['direction'] = 'down'
            elif (dx < 0):
                animation_state[id]['direction'] = 'left'
            elif (dx > 0):
                animation_state[id]['direction'] = 'right'
            else:
                animation_state[id]['is_moving'] = False

    current_time = time.time()
    for id in animation_state:
        if animation_state[id]['is_moving']:
            if current_time - animation_state[id]['last_update'] > 0.1:
                if id == '0':
                    frames = player1_animations[animation_state[id]['direction']]
                elif id == '1':
                    frames = player2_animations[animation_state[id]['direction']]
                else:
                    continue

                animation_state[id]['frame'] = (
                    animation_state[id]['frame'] + 1) % len(frames)
                animation_state[id]['last_update'] = current_time
        else:
            animation_state[id]['frame'] = 0


def draw_game(screen, game_state, animation_state):
    # Draw the map
    map_matrix = game_state['map']
    for row in range(len(map_matrix)):
        for col in range(len(map_matrix[0])):
            cell_value = map_matrix[row][col]
            color = BACKGROUND_COLOR
            if cell_value == 1:
                # screen.blit(rock_sprite, (col * TILE_SIZE,
                #             row * TILE_SIZE + HUD_HEIGHT))
                color = OBSTACLE_COLOR  # Unbreakable
            elif cell_value == 2:
                screen.blit(trunk_sprite, (col * TILE_SIZE,
                            row * TILE_SIZE + HUD_HEIGHT))
                color = BREAKABLE_COLOR  # Breakable
            elif cell_value == -2:
                color = BREAKING_COLOR  # Breaking
                pygame.draw.rect(screen, color, (col * TILE_SIZE,
                                 row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE))
            elif cell_value == 3:
                # screen.blit(mango_bomb_sprite, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT))
                color = BOMB_COLOR  # Bomb

            # pygame.draw.rect(screen, GRID_COLOR, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE), 1)

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
            pygame.draw.rect(
                screen, color, (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))

    # Draw players
    for id, (x,y) in game_state['players'].items():
        pixel_x = x * TILE_SIZE  # Calculate pixel_x here
        pixel_y = y * TILE_SIZE + HUD_HEIGHT  # Calculate pixel_y here

        direction = animation_state[id]['direction']
        frame = animation_state[id]['frame']
        if id == '0':
            sprite = player1_animations[direction][frame]
        elif id == '1':
            sprite = player2_animations[direction][frame]
        else:
            continue

        sprite_width, sprite_height = sprite.get_size()
        centralized_x = pixel_x + (TILE_SIZE - sprite_width) // 2
        centralized_y = pixel_y  # A altura já é a mesma, então não precisa ajustar
        # Use the player sprite at the calculated pixel coordinates
        screen.blit(sprite, (centralized_x, centralized_y))


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
        'down': [pygame.transform.scale(pygame.image.load(f'assets/caco-walking-down-animation/caco-walking-down-frame-{i}.png').convert_alpha(), (65, 80)) for i in range(1, 9)],
        'up': [pygame.transform.scale(pygame.image.load(f'assets/caco-walking-up-animation/caco-walking-up-frame-{i}.png').convert_alpha(), (65, 80)) for i in range(1, 9)],
        'left': [pygame.transform.scale(pygame.image.load(f'assets/caco-walking-left-animation/caco-walking-left-frame-{i}.png').convert_alpha(), (65, 80)) for i in range(1, 9)],
        'right': [pygame.transform.scale(pygame.image.load(f'assets/caco-walking-right-animation/caco-walking-right-frame-{i}.png').convert_alpha(), (65, 80)) for i in range(1, 9)],
    }
    return animations


def load_player2_animation_frames():
    animations = {
        'down': [pygame.transform.scale(pygame.image.load(f'assets/cobra-walking-right-animation/cobra-right-{i}.png').convert_alpha(), (75, 80)) for i in range(1, 9)],
        'up': [pygame.transform.scale(pygame.image.load(f'assets/cobra-walking-left-animation/cobra-left-{i}.png').convert_alpha(), (75, 80)) for i in range(1, 9)],
        'left': [pygame.transform.scale(pygame.image.load(f'assets/cobra-walking-left-animation/cobra-left-{i}.png').convert_alpha(), (75, 80)) for i in range(1, 9)],
        'right': [pygame.transform.scale(pygame.image.load(f'assets/cobra-walking-right-animation/cobra-right-{i}.png').convert_alpha(), (75, 80)) for i in range(1, 9)],
    }
    return animations


if __name__ == '__main__':
    import websockets
    asyncio.run(main())
