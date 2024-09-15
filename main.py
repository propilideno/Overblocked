import pygame
from enum import Enum
from math import ceil
import time
import sys

from game import *
from settings import *

def main():
    global lives, map

    pygame.init()

    # Initialize game
    reset_game()

    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bomberman Clone")

    # Create clock object to manage frame rate
    clock = pygame.time.Clock()
    start_time = time.time()

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

if __name__ == '__main__':
    main()
