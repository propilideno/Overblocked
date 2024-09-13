import pygame
from enum import Enum
from math import ceil
import time
import sys

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 50
GRID_WIDTH = 15  # 15 tiles wide
GRID_HEIGHT = 11  # 11 tiles high
HUD_HEIGHT = 50  # Height of the HUD (ignored in position tracking)
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT + HUD_HEIGHT  # Adding space for HUD
BACKGROUND_COLOR = (50, 150, 50)  # Green for the background
GRID_COLOR = (200, 200, 200)  # Light grey for the grid
BREAKABLE_COLOR = (139, 69, 19)   # Breakable objects (brown)
BOMB_COLOR = (0, 0, 0)  # Bombs are black
OBSTACLE_COLOR = (100, 100, 100)  # Dark grey for unbreakable obstacles
PLAYER_COLOR = (255, 0, 0)  # Red player
PLAYER_2_COLOR = (0, 0, 255)  # Blue player
HUD_COLOR = (0, 0, 0)  # Black for the HUD background
PRECISION = 3
TOLERANCE = 0.1  # 10% tolerance for movement alignment

EXPLOSION_GREEN_COLOR = (0, 255, 0)  # Green explosion
EXPLOSION_YELLOW_COLOR = (255, 255, 0)  # Yellow explosion

# Enum for movement types
class MovementType(Enum):
    NONE = 0
    LINEAR = 1
    DIAGONAL = 2

class GameController:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    PLACE_BOMB = 4

    key_map = {
        UP: [pygame.K_UP, pygame.K_w],
        DOWN: [pygame.K_DOWN, pygame.K_s],
        LEFT: [pygame.K_LEFT, pygame.K_a],
        RIGHT: [pygame.K_RIGHT, pygame.K_d],
        PLACE_BOMB: [pygame.K_SPACE]
    }

    def __init__(self, keys):
        self.keys = keys

    def __getitem__(self, direction):
        # Return True if any key associated with the direction is pressed
        return any(self.keys[key] for key in GameController.key_map[direction])

# Base class for all objects that need to know about tile size
class GameObject:
    def __init__(self, x, y):
        self.x = x  # Grid position
        self.y = y  # Grid position
        self.pixel_x = round(x * TILE_SIZE, PRECISION)  # Pixel position
        self.pixel_y = round(y * TILE_SIZE, PRECISION) + HUD_HEIGHT  # Adjusted for HUD

    def get_grid_position(self):
        return round(self.x, PRECISION), round(self.y, PRECISION)

    def update_pos(self, new_x, new_y):
        # Update the grid position and pixel position
        self.x = round(new_x, PRECISION)
        self.y = round(new_y, PRECISION)
        self.update_pixel_position()

    def update_pixel_position(self):
        self.pixel_x = round(self.x * TILE_SIZE, PRECISION)
        self.pixel_y = round(self.y * TILE_SIZE, PRECISION) + HUD_HEIGHT


    def draw(self, screen, color):
        pygame.draw.rect(screen, color, (self.pixel_x, self.pixel_y, TILE_SIZE, TILE_SIZE))

class GameMap(GameObject):
    def __init__(self, matrix):
        super().__init__(0, 0)  # Initialize at grid origin
        self.width = len(matrix[0])
        self.height = len(matrix)
        self.matrix = matrix

    def is_position_walkable(self, x, y):
        return not self.is_obstacle(x,y)

    def is_unbreakable_obstacle(self, grid_x, grid_y):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            return self.matrix[grid_y][grid_x] == 1
        return False

    def is_breakable_obstacle(self, grid_x, grid_y):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            return self.matrix[grid_y][grid_x] == 2
        return False

    def is_obstacle(self, grid_x, grid_y):
        if 0 <= grid_y < map.height and 0 <= grid_x < map.width:
            return map.matrix[grid_y][grid_x] in [1, 2]  # Unbreakable (1) or breakable (2)
        return True  # Out of bounds is considered an obstacle

    def draw(self, screen):
        for row in range(self.height):
            for col in range(self.width):
                color = BACKGROUND_COLOR
                if self.matrix[row][col] == 1:
                    color = OBSTACLE_COLOR  # Unbreakable
                elif self.matrix[row][col] == 2:
                    color = BREAKABLE_COLOR  # Breakable
                elif self.matrix[row][col] == 3:
                    color = BOMB_COLOR  # Bomb
                pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE))  # Adjust for HUD
                pygame.draw.rect(screen, GRID_COLOR, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE), 1)  # Grid lines

class Bomb(GameObject):
    def __init__(self, player_id, bomb_type, x, y):
        super().__init__(round(x), round(y))  # Initialize the Bomb's at the nearest grid
        self.player_id = player_id  # Store the player's ID
        self.bomb_type = bomb_type  # Type of bomb: green or yellow
        self.placed_at = time.time()  # Timestamp when the bomb was placed
        self.explosion_range = 3  # How far the explosion spreads
        self.is_exploded = False  # Track if the bomb has exploded
        self.explosion = None  # To store the explosion object

    def update(self):
        # Check if the bomb should explode
        if not self.is_exploded and time.time() - self.placed_at >= 3:  # 3 seconds delay
            self.explode()

    def explode(self):
        self.is_exploded = True
        # Remove the bomb from the map
        map.matrix[int(self.y)][int(self.x)] = 0  # Bomb removed from the grid
        
        # Remove bomb from the global bombs list and decrement the player's placed bomb count
        bombs.remove(self)
        placed_bombs[self.player_id] -= 1  # Decrement the count of placed bombs
        
        # Trigger the explosion, affecting the grid
        explosion_color = EXPLOSION_GREEN_COLOR if self.bomb_type == 'green' else EXPLOSION_YELLOW_COLOR
        self.explosion = Explosion(self.x, self.y, self.explosion_range, explosion_color)
        explosions.append(self.explosion)  # Add the explosion to the global list

        self.check_explosion_destruction()

    def check_explosion_destruction(self):
        # Check if the explosion affects any players or breakable blocks
        for sector in self.explosion.sectors:  # Only check sectors of its own explosion
            grid_x, grid_y = int(sector[0]), int(sector[1])

            # Check if any player is hit
            for i, player in enumerate(players):
                if int(player.x) == grid_x and int(player.y) == grid_y and player.can_be_damaged == True:
                    lives[i] -= 1
                    player.can_be_damaged = False

                    print(f"Player {i+1} hit! Lives left: {lives[i]}")
                    if lives[i] == 0:
                        print(f"Player {i+1} has lost all lives. Game over!")
                        pygame.quit()
                        sys.exit()
                    reset_game()

            # Check if there is a breakable block in the sector
            if map.matrix[grid_y][grid_x] == 2:  # Breakable block (now back to matrix[y][x] access)
                map.matrix[grid_y][grid_x] = 0  # Destroy the block

    def draw(self, screen,color=BOMB_COLOR):
        super().draw(screen,color)  # Use GameObject's draw method


class Explosion(GameObject):
    def __init__(self, x, y, explosion_range, color):
        super().__init__(x, y)  # Initialize the explosion's position
        self.range = explosion_range
        self.color = color
        self.sectors = self.calculate_sectors()
        self.start_time = time.time()

    def calculate_sectors(self):
        sectors = [[self.x, self.y]]  # The bomb's position

        # Helper to calculate explosion in one direction
        def spread_in_direction(dx, dy):
            for i in range(1, self.range + 1):
                grid_x = self.x + i * dx
                grid_y = self.y + i * dy

                # Verifica se há um obstáculo inquebrável
                if map.is_unbreakable_obstacle(grid_x, grid_y):
                    break  # Para a explosão ao encontrar um obstáculo inquebrável

                # Verifica se há um bloco quebrável
                if map.is_breakable_obstacle(grid_x, grid_y):
                    map.matrix[grid_y][grid_x] = 0  # Destrói o bloco quebrável
                    sectors.append([grid_x, grid_y])  # Adiciona o bloco à lista de setores afetados
                    break  # Para a explosão após destruir o bloco

                # Se não houver obstáculo, continua adicionando o setor
                sectors.append([grid_x, grid_y])



        # Spread explosion in four directions
        spread_in_direction(1, 0)  # Right
        spread_in_direction(-1, 0)  # Left
        spread_in_direction(0, 1)  # Down
        spread_in_direction(0, -1)  # Up

        return sectors

    def update(self):
        # Remove the explosion after its duration
        if time.time() - self.start_time > 1:  # Explosion lasts for 1 second
            explosions.remove(self)

    def draw(self, screen):
        # Draw the explosion sectors
        for sector in self.sectors:
            pixel_x = sector[0] * TILE_SIZE
            pixel_y = sector[1] * TILE_SIZE + HUD_HEIGHT
            pygame.draw.rect(screen, self.color, (pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))

    def is_player_in_explosion(self, player):
        # Use TOLERANCE to check if the player is within the explosion area
        for sector in self.sectors:
            if (abs(player.x - sector[0]) <= TOLERANCE) and (abs(player.y - sector[1]) <= TOLERANCE):
                return True
        return False

class Player(GameObject):
    def __init__(self, x, y, bomb_type, player_id):
        super().__init__(x, y)
        self.speed = 0.05  # Movement speed in tile units per update
        self.bomb_type = bomb_type  # Type of bombs the player can place
        self.player_id = player_id  # Player ID
        self.can_be_damaged = True

    def place_bomb(self):
        # Place bomb at the nearest grid position (round the player's current position)
        if placed_bombs[self.player_id] < 3 and map.matrix[int(self.y)][int(self.x)] != 3:
            bomb = Bomb(self.player_id, self.bomb_type, round(self.x), round(self.y))
            bombs.append(bomb)  # Add the bomb to the global bombs list
            placed_bombs[self.player_id] += 1  # Increment the count of placed bombs

    def move(self, controller):
        # Initialize new positions as current positions
        new_x, new_y = self.x, self.y

        # Handle movement using GameController keys
        if controller[GameController.UP]:
            new_y = self.y - self.speed
            if map.is_position_walkable(int(self.x), int(new_y)):
                if int(self.x) == self.x:
                    self.y = round(new_y, PRECISION)

        if controller[GameController.DOWN]:
            new_y = self.y + self.speed
            if map.is_position_walkable(int(self.x), ceil(new_y)):
                if int(self.x) == self.x:
                    self.y = round(new_y, PRECISION)

        if controller[GameController.LEFT]:
            new_x = self.x - self.speed
            if map.is_position_walkable(int(new_x), int(self.y)):
                if int(self.y) == self.y:
                    self.x = round(new_x, PRECISION)

        if controller[GameController.RIGHT]:
            new_x = self.x + self.speed
            if map.is_position_walkable(ceil(new_x), int(self.y)):
                if int(self.y) == self.y:
                    self.x = round(new_x, PRECISION)

        # Update player position after calculating new positions
        super().update_pixel_position()

    def check_collision_with_explosions(self):
        for explosion in explosions:
            if (explosion.is_player_in_explosion(self) and self.can_be_damaged == True):
                lives[self.player_id] -= 1
                self.can_be_damaged = False # This magically work because player ir re-instanced every time he takes damage
                print(f"Player {self.player_id + 1} hit by explosion! Lives left: {lives[self.player_id]}")
                if lives[self.player_id] == 0:
                    print(f"Player {self.player_id + 1} has lost all lives. Game over!")
                    pygame.quit()
                    sys.exit()
                reset_game()  # Reset game after a player is hit

# Reset the game when a player is hit
def reset_game():
    global players, bombs, explosions, placed_bombs

    # Clear bombs and explosion
    bombs.clear()
    explosions.clear()
    placed_bombs = [0, 0]

    # Replace players
    players = [
        Player(1, 1, "green", 0),
        Player(GRID_WIDTH - 2, GRID_HEIGHT - 2, "yellow", 1)
    ]


# Function to draw the HUD
def draw_hud(screen, timer):
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

# Global list to track bombs and explosions
bombs = []
explosions = []
players = []

placed_bombs = [0, 0]  # Track placed bombs per player (2 players)
lives = [3, 3]  # 3 lives for each player


# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomberman Clone")

# Initialize game
reset_game()

# Create clock object to manage frame rate
clock = pygame.time.Clock()
start_time = time.time()

map = GameMap([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 2, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 2, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
])

# Main loop
running = True
while running:
    dt = clock.tick(60)  # Delta time in milliseconds
    current_time = time.time() - start_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # In the game loop, update bombs and explosions
    for bomb in bombs:
        bomb.update()

    for explosion in explosions:
        explosion.update()

    # Get key presses
    keys = pygame.key.get_pressed()
    controller = GameController(keys)

    # Key binding to place a bomb
    if controller[GameController.PLACE_BOMB]:
        players[0].place_bomb()  # Player 1 is active, Player 2 is static

    # Move player with key inputs
    players[0].move(controller)

    # Check if player collides with any explosions
    for player in players:
        player.check_collision_with_explosions()

    # Clear the screen and redraw the grid and HUD
    screen.fill(BACKGROUND_COLOR)
    draw_hud(screen, current_time)
    map.draw(screen)

    # Draw bombs
    for bomb in bombs:
        bomb.draw(screen)

    # Draw explosions
    for explosion in explosions:
        explosion.draw(screen)

    # Draw players
    players[0].draw(screen, PLAYER_COLOR)
    players[1].draw(screen, PLAYER_2_COLOR)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
