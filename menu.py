import pygame
import sys

# Inicializa o pygame
pygame.init()

# Definir cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Dimensões da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Menu do Jogo')

# Definir fonte
font = pygame.font.Font(None, 74)

# Função para o menu principal
def main_menu():
    while True:
        screen.fill(WHITE)

        # Exibe as opções de menu
        draw_text('Modo Solo', font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text('Modo Multiplayer Local', font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text('Modo Multiplayer Online', font, BLACK, screen, SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 4) * 3)

        # Captura os eventos do teclado
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Pressiona "1" para modo solo
                    start_solo_mode()
                if event.key == pygame.K_2:  # Pressiona "2" para multiplayer local
                    start_multiplayer_local_mode()
                if event.key == pygame.K_3:  # Pressiona "3" para multiplayer online
                    start_multiplayer_online_mode()

        pygame.display.update()

# Funções para cada modo de jogo
def start_solo_mode():
    print("Iniciando Modo Solo...")
    reset_game()  # Reinicializa o jogo
    game_loop()   # Inicia o loop principal do jogo

def start_multiplayer_local_mode():
    print("Iniciando Modo Multiplayer Local...")
    reset_game()  # Aqui pode ter uma lógica de inicialização diferente para multiplayer local
    game_loop()

def start_multiplayer_online_mode():
    print("Iniciando Modo Multiplayer Online...")
    # Aqui você pode implementar a lógica de conexão com servidores ou criação de sala
    reset_game()
    game_loop()

# Função para desenhar o texto na tela
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

# Função para o menu principal
def main_menu():
    while True:
        screen.fill(WHITE)
        
        # Exibir opções do menu
        draw_text('Modo Solo', font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        draw_text('Modo Multiplayer Local', font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        draw_text('Modo Multiplayer Online', font, BLACK, screen, SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 4) * 3)
        
        # Capturar eventos do teclado
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Pressiona "1" para modo solo
                    start_solo_mode()
                if event.key == pygame.K_2:  # Pressiona "2" para modo multiplayer local
                    start_multiplayer_local_mode()
                if event.key == pygame.K_3:  # Pressiona "3" para modo multiplayer online
                    start_multiplayer_online_mode()

        pygame.display.update()

# Funções para cada modo de jogo
def start_solo_mode():
    print("Iniciando Modo Solo...")
    # Aqui você pode chamar a lógica do seu modo solo

def start_multiplayer_local_mode():
    print("Iniciando Modo Multiplayer Local...")
    # Aqui você pode chamar a lógica do seu modo multiplayer local

def start_multiplayer_online_mode():
    print("Iniciando Modo Multiplayer Online...")
    # Aqui você pode chamar a lógica do seu modo multiplayer online

# Iniciar o menu principal
main_menu()
