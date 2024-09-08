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
HUD_COLOR = (0, 0, 0)  # Black for the HUD background
PRECISION = 3
TOLERANCE = 0.1  # 10% tolerance for movement alignment

EXPLOSION_GREEN_COLOR = (0, 255, 0)  # Green explosion
EXPLOSION_YELLOW_COLOR = (255, 255, 0)  # Yellow explosi

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

# Grid class that manages the grid, obstacles, and their positions
class GameMap(GameObject):
    def __init__(self, matrix):
        super().__init__(0, 0)  # Initialize at grid origin
        self.width = len(matrix[0])
        self.height = len(matrix)
        self.matrix = matrix

    def is_position_walkable(self, x, y):
        # Check if a grid position is within bounds and walkable
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.matrix[y][x] == 0
        return False

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
    def __init__(self, player, bomb_type, x, y):
        # Initialize the Bomb's position from GameObject (round to nearest grid position)
        super().__init__(int(round(x)), int(round(y)))
        self.player = player  # The player who placed the bomb
        self.bomb_type = bomb_type  # Type of bomb: green or yellow
        self.placed_at = time.time()  # Timestamp when the bomb was placed
        self.explosion_range = 3  # How far the explosion spreads
        self.is_exploded = False  # Track if the bomb has exploded

    def update(self):
        # Check if the bomb should explode
        if not self.is_exploded and time.time() - self.placed_at >= 3:  # 3 seconds delay
            self.explode()

    def explode(self):
        self.is_exploded = True
        # Remove the bomb from the map
        map.matrix[int(self.y)][int(self.x)] = 0  # Bomb removed from the grid
        
        # Remove bomb from the global bombs list
        bombs.remove(self)
        
        # Trigger the explosion, affecting the grid
        explosion_color = EXPLOSION_GREEN_COLOR if self.bomb_type == 'green' else EXPLOSION_YELLOW_COLOR
        explosion = Explosion(self.x, self.y, self.explosion_range, explosion_color)
        explosions.append(explosion)  # Add the explosion to the global list

        # Check if the explosion hits any players or blocks
        self.check_explosion_destruction()

    def check_explosion_destruction(self):
        # Check if the explosion affects any players or breakable blocks
        for explosion in explosions:
            for sector in explosion.sectors:
                # Ensure we're using integers to access the grid
                grid_x, grid_y = int(sector[0]), int(sector[1])
                
                # Check if the player is in the explosion sector
                if int(player.x) == grid_x and int(player.y) == grid_y:
                    # Player is hit by the explosion, game over
                    print("Player destroyed by explosion!")
                    pygame.quit()
                    sys.exit()

                # Check if there is a breakable block in the sector
                if map.matrix[grid_y][grid_x] == 2:  # Breakable block
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
        # Spread explosion in four directions
        for i in range(1, self.range + 1):
            sectors.append([self.x + i, self.y])  # Right
            sectors.append([self.x - i, self.y])  # Left
            sectors.append([self.x, self.y + i])  # Down
            sectors.append([self.x, self.y - i])  # Up
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
            
class Player(GameObject):
    def __init__(self, x, y, bomb_type):
        super().__init__(x, y)
        self.speed = 0.05  # Movement speed in tile units per update
        self.bomb_limit = 1  # Number of bombs the player can place at a time
        self.bomb_type = bomb_type  # Type of bombs the player can place

    def place_bomb(self):
        if self.bomb_limit > 0:
            bomb = Bomb(self, self.bomb_type, self.x, self.y)
            bombs.append(bomb)  # Add the bomb to the global bombs list
            self.bomb_limit -= 1

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

# Function to draw the HUD
def draw_hud(screen, player):
    # Create a black background for the HUD
    pygame.draw.rect(screen, HUD_COLOR, (0, 0, SCREEN_WIDTH, HUD_HEIGHT))
    # Display the player's position on the HUD
    font = pygame.font.SysFont(None, 36)
    grid_position = player.get_grid_position()
    pixel_position = (round(player.pixel_x, PRECISION), round(player.pixel_y - HUD_HEIGHT, PRECISION))
    text = font.render(f"Grid Pos: {grid_position} | Pixel Pos: {pixel_position}", True, (255, 255, 255))  # White text
    screen.blit(text, (10, 10))

# Global list to track bombs and explosions
bombs = []
explosions = []

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomberman Clone")

# Create grid and player objects
player = Player(1, 1, "green")

# Create clock object to manage frame rate
clock = pygame.time.Clock()

map = GameMap([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
])

# Main loop
running = True
while running:
    dt = clock.tick(60)  # Delta time in milliseconds

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
        player.place_bomb()

    # Move player with key inputs
    player.move(controller)

    # Clear the screen and redraw the grid and HUD
    screen.fill(BACKGROUND_COLOR)
    draw_hud(screen, player)  # Draw HUD with player's position
    map.draw(screen)

    # Draw bombs
    for bomb in bombs:
        bomb.draw(screen)

    # Draw explosions
    for explosion in explosions:
        explosion.draw(screen)

    # Draw the player on top of the grid
    player.draw(screen, PLAYER_COLOR)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
