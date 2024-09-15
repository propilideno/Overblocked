import pygame
import threading
import time
import sys
import copy
from enum import Enum
from math import ceil

from settings import *

# Global lists and variables
bombs = []
explosions = []
players = []
placed_bombs = [0, 0]  # Track placed bombs per player (2 players)
current_map_number = 0  # To keep track of the current map

def reset_game():
    global lives
    lives = [PLAYER_LIVES, PLAYER_LIVES]
    reset_round()

def reset_round():
    # Reset players' positions instead of recreating them
    for player in players:
        if player.player_id == 0:
            player.__init__(1, 1, "BOMB_TYPE_1", 0)
        elif player.player_id == 1:
            player.__init__(map.width - 2, map.height - 2, "BOMB_TYPE_2", 1)
    explosions.clear()
    bombs.clear()
    placed_bombs[:] = [0,0]
    map.next_map()

# Enum for movement types
class MovementType(Enum):
    NONE = 0
    LINEAR = 1
    DIAGONAL = 2

class GameController:
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    PLACE_BOMB = 'place_bomb'

    def __init__(self, input_data):
        self.input_data = input_data

    def __getitem__(self, direction):
        return self.input_data.get(direction, False)

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

class GameMap(GameObject):
    def __init__(self, map_number=0):
        super().__init__(0, 0)  # Initialize at grid origin
        self.maps = [
            # Map 1
            [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 2, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
                [1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 2, 0, 2, 0, 0, 2, 0, 0, 0, 2, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 2, 0, 1],
                [1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ],
            # Map 2
            [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ],
            # Map 3
            [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1],
                [1, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 2, 0, 0, 2, 0, 2, 2, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ]
        ]
        self.map_number = map_number % len(self.maps)
        self.matrix = self.maps[self.map_number]
        self.width = len(self.matrix[0])
        self.height = len(self.matrix)

    def next_map(self):
        self.map_number = (self.map_number + 1) % len(self.maps)
        self.return_map_to_original_state()

    def is_position_walkable(self, x, y, player):
        return not self.is_obstacle(x,y, player)

    def is_unbreakable_obstacle(self, grid_x, grid_y):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            return self.matrix[grid_y][grid_x] in [1,-2]
        return False

    def is_breakable_obstacle(self, grid_x, grid_y):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            return self.matrix[grid_y][grid_x] == 2
        return False

    def is_obstacle(self, grid_x, grid_y, player):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            if player.just_placed_bomb is not None:
                if self.matrix[grid_y][grid_x] == 3:
                    print("é bomba")
                    if (player.x <= player.just_placed_bomb[0] + 1 and
                        player.x >= player.just_placed_bomb[0] - 1 and
                        player.y <= player.just_placed_bomb[1] + 1 and
                        player.y >= player.just_placed_bomb[1] - 1):
                        print("permitido")
                        return False
            return self.matrix[grid_y][grid_x] in [1, 2, 3]
        return True  # Out of bounds is considered an obstacle

    def return_map_to_original_state(self):
        self.matrix = copy.deepcopy(self.maps[self.map_number])

class Bomb(GameObject):
    def __init__(self, player_id, bomb_type, x, y):
        super().__init__(round(x), round(y))  # Initialize the Bomb's at the nearest grid
        self.player_id = player_id  # Store the player's ID
        self.bomb_type = bomb_type  # Type of bomb: green or yellow
        self.placed_at = time.time()  # Timestamp when the bomb was placed
        self.explosion_range = BOMB_EXPLOSION_RANGE  # How far the explosion spreads
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
        self.explosion = Explosion(self.x, self.y, self.explosion_range, self.bomb_type)
        explosions.append(self.explosion)  # Add the explosion to the global list

        self.check_explosion_destruction()

    def check_explosion_destruction(self):
        # Check if the explosion affects any players or breakable blocks
        for sector in self.explosion.sectors:  # Only check sectors of its own explosion
            grid_x, grid_y = int(sector[0]), int(sector[1])

            # Check if any player is hit
            for i, player in enumerate(players):
                if int(player.x) == grid_x and int(player.y) == grid_y:
                    lives[i] -= 1
                    print(f"Player {i+1} hit! Lives left: {lives[i]}")
                    if lives[i] == 0:
                        print(f"Player {i+1} has lost all lives. Game over!")
                        reset_game()
                    reset_round()

            # Check if there is a breakable block in the sector
            if map.matrix[grid_y][grid_x] in [-2,2]:  # Breakable block (now back to matrix[y][x] access)
                map.matrix[grid_y][grid_x] = 0  # Destroy the block

class Explosion(GameObject):
    def __init__(self, x, y, explosion_range, bomb_type):
        super().__init__(x, y)  # Inicializa a posição da explosão
        self.range = explosion_range
        self.bomb_type = bomb_type
        self.blocks_to_destroy = []  # Lista para armazenar blocos a serem destruídos
        self.sectors = self.calculate_sectors()
        self.start_time = time.time()

    def calculate_sectors(self):
        sectors = [[self.x, self.y]]  # Posição inicial da bomba

        # Função auxiliar para calcular a explosão em uma direção
        def spread_in_direction(dx, dy):
            for i in range(1, self.range + 1):
                grid_x = self.x + i * dx
                grid_y = self.y + i * dy

                # Verifica se há um obstáculo inquebrável
                if map.is_unbreakable_obstacle(grid_x, grid_y):
                    break  # Para a explosão ao encontrar um obstáculo inquebrável

                # Verifica se há um bloco quebrável
                if map.is_breakable_obstacle(grid_x, grid_y):
                    map.matrix[grid_y][grid_x] = -2
                    #sectors.append([grid_x, grid_y])  # Adiciona o bloco à lista de setores afetados
                    self.blocks_to_destroy.append((grid_x, grid_y))  # Marca o bloco para destruição
                    break  # Para a explosão após destruir o bloco

                # Se não houver obstáculo, continua adicionando o setor
                sectors.append([grid_x, grid_y])

        # Propaga a explosão nas quatro direções
        spread_in_direction(1, 0)  # Direita
        spread_in_direction(-1, 0)  # Esquerda
        spread_in_direction(0, 1)  # Baixo
        spread_in_direction(0, -1)  # Cima

        return sectors

    def update(self):
        # Remove a explosão após sua duração
        if time.time() - self.start_time > 0.4:  # A explosão dura 1 segundo
            # Destrói os blocos após a explosão terminar
            for (grid_x, grid_y) in self.blocks_to_destroy:
                map.matrix[grid_y][grid_x] = 0  # Destrói o bloco marcado
            explosions.remove(self)

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
        self.can_place_bomb = True
        self.just_placed_bomb = None

    def place_bomb(self):
        # Place bomb at the nearest grid position (round the player's current position)
        if placed_bombs[self.player_id] < 3 and map.matrix[int(self.y)][int(self.x)] != 3 and self.can_place_bomb:
            x_bomb = round(self.x)
            y_bomb = round(self.y)
            #print("place bomb at ", x_bomb, y_bomb)
            bomb = Bomb(self.player_id, self.bomb_type, x_bomb, y_bomb)
            bombs.append(bomb)  # Add the bomb to the global bombs list
            
            # Permite o player atravessar a bomba temporariamente
            self.just_placed_bomb = (x_bomb, y_bomb)
            print("just placed bomb value: ", self.just_placed_bomb)
            
            map.matrix[y_bomb][x_bomb] = 3  # Mark the grid as having a bomb
            self.can_place_bomb = False
            placed_bombs[self.player_id] += 1  # Increment the count of placed bombs
            # Reativa a capacidade de colocar bomba após 3 segundos (por exemplo)
            threading.Timer(3, self.reactivate_bomb_placement).start()

    def reactivate_bomb_placement(self):
        self.can_place_bomb = True

    def move(self, controller):
        new_x, new_y = self.x, self.y
        if self.just_placed_bomb is not None:
            if (self.x >= self.just_placed_bomb[0] + 1 or self.x <= self.just_placed_bomb[0] - 1 or
                    self.y >= self.just_placed_bomb[1] + 1 or self.y <= self.just_placed_bomb[1] - 1):
                self.just_placed_bomb = None

        # Handle movement using GameController input
        if controller['up']:
            new_y = self.y - self.speed
            if map.is_position_walkable(int(self.x), int(new_y), self):
                if int(self.x) == self.x:
                    self.y = round(new_y, PRECISION)

        if controller['down']:
            new_y = self.y + self.speed
            if map.is_position_walkable(int(self.x), ceil(new_y), self):
                if int(self.x) == self.x:
                    self.y = round(new_y, PRECISION)

        if controller['left']:
            new_x = self.x - self.speed
            if map.is_position_walkable(int(new_x), int(self.y), self):
                if int(self.y) == self.y:
                    self.x = round(new_x, PRECISION)

        if controller['right']:
            new_x = self.x + self.speed
            if map.is_position_walkable(ceil(new_x), int(self.y), self):
                if int(self.y) == self.y:
                    self.x = round(new_x, PRECISION)

        #if self.check_collision_with_explosions:
        #    reset_round()    # Not working

        # Update player position after calculating new positions
        self.update_pixel_position()

    def check_collision_with_explosions(self):
        for explosion in explosions:
            if (explosion.is_player_in_explosion(self)):
                lives[self.player_id] -= 1
                print(f"Player {self.player_id + 1} hit by explosion! Lives left: {lives[self.player_id]}")
                if lives[self.player_id] == 0:
                    print(f"Player {self.player_id + 1} has lost all lives. Game over!")
                    reset_game()
                return True
            else:
                return False

# Initialize game_map globally
map = GameMap()
reset_game()

# Export necessary variables and classes
__all__ = [
    'GameController', 'GameMap', 'Player', 'bombs', 'explosions', 'players',
    'placed_bombs', 'lives', 'reset_game', 'map'
]
