import socket
import pickle
import pygame
import sys

# Configurações do cliente
HOST = 'localhost' # ATENÇÃO !!!!!!!!!!!! Insira aqui, entre aspas, o IP do computador que irá hostear o jogo.
PORT = 1313

# Dimensões da tela
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Configurações do jogador
PLAYER_RADIUS = 10
colorR = random.randint(0, 255)
colorG = random.randint(0, 255)
colorB = random.randint(0, 255)

# Configurações do tiro
SHOT_RADIUS = 6
SHOT_SPEED = 8

# Lista para armazenar os jogadores eliminados
eliminated_players = []

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Conexão com o servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((HOST, PORT))
print('Conexão estabelecida com o servidor')

# Loop principal
running = True
player_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Posição inicial do jogador
shots = {}

while running:
    # Processamento de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Captura a entrada do teclado
    keys = pygame.key.get_pressed()

    # Envia os dados para o servidor
    movement = ''
    shooting = False
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if keys[pygame.K_w]:
        movement = 'UP'
    elif keys[pygame.K_s]:
        movement = 'DOWN'
    elif keys[pygame.K_a]:
        movement = 'LEFT'
    elif keys[pygame.K_d]:
        movement = 'RIGHT'
    elif keys[pygame.K_SPACE]:
        shooting = True

    data = pickle.dumps((movement, shooting, mouse_x, mouse_y))
    server_socket.sendall(data)

    # Recebe os dados atualizados do servidor
    data_received = server_socket.recv(4096)

    if not data_received:  # Verifica se não há dados recebidos
        continue

    try:
        # Desempacota os valores recebidos corretamente
        players, received_shots, game_over, winner = pickle.loads(data_received)

        # Verifica se o jogador foi eliminado
        if game_over:
            print("Game Over! Você foi eliminado.")
            screen.fill((0, 0, 0))  # Preenche a tela com a cor preta
            # Configuração do texto
            font = pygame.font.Font(None, 36)
            text = font.render("Game Over! Você foi eliminado.", True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (1024 // 2, 768 // 2)

            # Desenha o texto na tela
            screen.blit(text, text_rect)

            pygame.display.flip()  # Atualiza a tela
            pygame.time.wait(3000)  # Espera 3 segundos antes de fechar a janela
            pygame.quit()
            sys.exit()
    except pickle.UnpicklingError as e:
        print("Erro ao desempacotar os dados recebidos:", e)
        continue

    # Verifica colisões entre jogadores e tiros
        for player_x, player_y in players.values():
            for shot_player_id, shot_x, shot_y, _, _ in received_shots:
                # Verifica se o tiro foi disparado pelo jogador atual
                if shot_player_id == player_id:
                    continue

                distance = ((player_x - shot_x) ** 2 + (player_y - shot_y) ** 2) ** 0.5
                if distance <= PLAYER_RADIUS + SHOT_RADIUS:
                    print("Game Over!")
                    pygame.time.wait(3000)  # Espera 3 segundos antes de fechar a janela
                    pygame.quit()
                    sys.exit()

    # Renderiza a tela
    screen.fill((0, 0, 0))

    if len(players) > 0:  # Verifica se há jogadores na lista
        # Desenha os jogadores
        for player_x, player_y in players.values():
            pygame.draw.circle(screen, (colorR, colorG, colorB), (player_x, player_y), PLAYER_RADIUS)

    # Desenha os tiros
    for shot_x, shot_y in received_shots:
        pygame.draw.circle(screen, (0, 255, 0), (int(shot_x), int(shot_y)), SHOT_RADIUS)

    pygame.display.flip()
    clock.tick(60)


# Encerra a conexão com o servidor
server_socket.close()
print('Conexão encerrada.')
