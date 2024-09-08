import pygame
from enum import Enum

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
OBSTACLE_COLOR = (100, 100, 100)  # Dark grey for unbreakable obstacles
PLAYER_COLOR = (255, 0, 0)  # Red player
HUD_COLOR = (0, 0, 0)  # Black for the HUD background
PRECISION = 3
TOLERANCE = 0.1  # 10% tolerance for movement alignment

# Enum for movement types
class MovementType(Enum):
    NONE = 0
    LINEAR = 1
    DIAGONAL = 2

# Class for handling game settings
class GameSettings:
    UP = pygame.K_UP or pygame.K_w
    DOWN = pygame.K_DOWN or pygame.K_s
    LEFT = pygame.K_LEFT or pygame.K_a
    RIGHT = pygame.K_RIGHT or pygame.K_d

# Base class for all objects that need to know about tile size
class GameObject:
    def __init__(self, x, y):
        self.x = x  # grid position
        self.y = y  # grid position
        self.pixel_x = round(x * TILE_SIZE, PRECISION)  # Pixel position
        self.pixel_y = round(y * TILE_SIZE, PRECISION) + HUD_HEIGHT  # Adjusted for HUD

    def update_pixel_position(self):
        self.pixel_x = round(self.x * TILE_SIZE, PRECISION)
        self.pixel_y = round(self.y * TILE_SIZE, PRECISION) + HUD_HEIGHT  # Adjust for HUD

    def get_grid_position(self):
        # Return grid position by ignoring the precision
        return round(self.x, PRECISION), round(self.y, PRECISION)

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, (self.pixel_x, self.pixel_y, TILE_SIZE, TILE_SIZE))

# Grid class that manages the grid, obstacles, and their positions
class Grid(GameObject):
    def __init__(self, width, height):
        super().__init__(0, 0)  # Initialize at grid origin
        self.width = width
        self.height = height
        self.grid_matrix = self.create_grid_with_obstacles()

    def create_grid_with_obstacles(self):
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Add edge obstacles
        for x in range(self.width):
            grid[0][x] = 1  # Top edge
            grid[self.height-1][x] = 1  # Bottom edge
        for y in range(self.height):
            grid[y][0] = 1  # Left edge
            grid[y][self.width-1] = 1  # Right edge
        
        # Add central unbreakable obstacles (like in Bomberman)
        for x in range(2, self.width-1, 2):
            for y in range(2, self.height-1, 2):
                grid[y][x] = 1  # 1 represents unbreakable obstacle
        return grid

    def is_position_walkable(self, grid_x, grid_y):
        # Check if a grid position is within bounds and walkable
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid_matrix[grid_y][grid_x] == 0
        return False

    def draw(self, screen):
        for row in range(self.height):
            for col in range(self.width):
                color = BACKGROUND_COLOR if self.grid_matrix[row][col] == 0 else OBSTACLE_COLOR
                pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE))  # Adjust for HUD
                pygame.draw.rect(screen, GRID_COLOR, (col * TILE_SIZE, row * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE), 1)  # Grid lines

# Player class that inherits from GameObject
class Player(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 0.05  # Movement speed in tile units per update

    def allowed_movement(self, direction, grid):
        # For now, assume all movement is LINEAR
        return MovementType.LINEAR

    def move(self, keys, grid):
        # Handle movement using GameSettings keys
        if keys[GameSettings.UP]:
            new_y = self.y - self.speed
            if grid.is_position_walkable(int(self.x), int(new_y)):
                if int(self.x) == self.x:
                    self.y = round(new_y, PRECISION)

        if keys[GameSettings.DOWN]:
            new_y = self.y + self.speed
            if grid.is_position_walkable(int(self.x), int(new_y + 0.999)):  # Check next full tile down
                if int(self.x) == self.x:
                    self.y = round(new_y, PRECISION)

        if keys[GameSettings.LEFT]:
            new_x = self.x - self.speed
            if grid.is_position_walkable(int(new_x), int(self.y)):
                if int(self.y) == self.y:
                    self.x = round(new_x, PRECISION)

        if keys[GameSettings.RIGHT]:
            new_x = self.x + self.speed
            if grid.is_position_walkable(int(new_x + 0.999), int(self.y)):  # Check next full tile to the right
                if int(self.y) == self.y:
                    self.x = round(new_x, PRECISION)

        # Update pixel position after movement
        self.update_pixel_position()

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

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomberman Clone")

# Create grid and player objects
grid = Grid(GRID_WIDTH, GRID_HEIGHT)
player = Player(1, 1)

# Create clock object to manage frame rate
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    dt = clock.tick(60)  # Delta time in milliseconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key presses
    keys = pygame.key.get_pressed()

    # Move player with key inputs
    player.move(keys, grid)

    # Clear the screen and redraw the grid and HUD
    screen.fill(BACKGROUND_COLOR)
    draw_hud(screen, player)  # Draw HUD with player's position
    grid.draw(screen)

    # Draw the player on top of the grid
    player.draw(screen, PLAYER_COLOR)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
