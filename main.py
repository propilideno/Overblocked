import pygame
from time import sleep

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 40
GRID_WIDTH = 15
GRID_HEIGHT = 11
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT
BACKGROUND_COLOR = (50, 50, 50)  # Dark grey
GRID_COLOR = (200, 200, 200)  # Light grey

# Game classes
class Grid:
    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size

    def draw(self, screen):
        for x in range(0, self.width * self.tile_size, self.tile_size):
            for y in range(0, self.height * self.tile_size, self.tile_size):
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

class Player:
    def __init__(self, color, x, y, tile_size, grid):
        self.color = color
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.grid = grid

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= 1
        if keys[pygame.K_RIGHT] and self.x < self.grid.width - 1:
            self.x += 1
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= 1
        if keys[pygame.K_DOWN] and self.y < self.grid.height - 1:
            self.y += 1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x * self.tile_size, self.y * self.tile_size, self.tile_size, self.tile_size))

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bomberman Clone")

# Create grid and player objects
grid = Grid(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE)
player = Player((255, 0, 0), 1, 1, TILE_SIZE, grid)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key presses
    keys = pygame.key.get_pressed()

    # Move player
    player.move(keys)

    # Fill screen with background color (flexible space)
    screen.fill(BACKGROUND_COLOR)

    # Draw grid and player
    grid.draw(screen)
    player.draw(screen)

    # Update display
    pygame.display.flip()

    sleep(0.1)

# Quit Pygame
pygame.quit()
