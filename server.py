import socket
import pickle
import threading

# Configurações do servidor
HOST = 'localhost'
PORT = 8000

# Dimensões da tela
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Configurações do jogador
PLAYER_RADIUS = 10
PLAYER_SPEED = 5
SHOOT_COOLDOWN = 30  # Tempo de recarga da arma (em frames)

# Configurações do tiro
SHOT_SPEED = 5
SHOT_RADIUS = 5

# Inicialização do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)  # Aceita até 2 clientes

# Lista para armazenar as informações dos jogadores conectados
players = {}

# Lista para armazenar as informações dos tiros disparados
shots = []

# Lista para armazenar os jogadores eliminados
eliminated_players = set()

# Função para lidar com a conexão de um cliente
def handle_client_connection(client_socket, player_id):
    # Posição inicial do jogador
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2

    # Tempo de recarga inicial da arma
    shoot_cooldown = 0

    # Loop principal para lidar com as ações do jogador
    while True:
        try:
            # Recebe os dados do jogador
            data = client_socket.recv(1024)
            if not data:
                break

            # Desserializa os dados recebidos
            movement, shooting, mouse_x, mouse_y = pickle.loads(data)

            # Atualiza a posição do jogador
            if movement == 'UP':
                player_y -= PLAYER_SPEED
            elif movement == 'DOWN':
                player_y += PLAYER_SPEED
            elif movement == 'LEFT':
                player_x -= PLAYER_SPEED
            elif movement == 'RIGHT':
                player_x += PLAYER_SPEED

            # Verifica os limites da tela para o jogador
            player_x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, player_x))
            player_y = max(PLAYER_RADIUS, min(SCREEN_HEIGHT - PLAYER_RADIUS, player_y))

            # Verifica se o jogador colidiu com algum tiro
            collision = False
            for shot_player_id, shot_x, shot_y, _, _ in shots:
                dx = player_x - shot_x
                dy = player_y - shot_y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if (
                    distance <= PLAYER_RADIUS + SHOT_RADIUS and
                    shot_player_id != player_id
                ):
                    # O jogador colidiu com um tiro, então ele perde o jogo
                    game_over = True
                    winner = 'Opponent'
                    collision = True
                    break

            # Atualiza as informações de game_over e winner
            if collision:
                game_over = True
                winner = 'Opponent'
                # Adiciona o jogador eliminado à lista de eliminados
                eliminated_players.add(player_id)
            else:
                game_over = False
                winner = None

            # Atualiza o tempo de recarga da arma
            if shoot_cooldown > 0:
                shoot_cooldown -= 1

            # Dispara um tiro
            if shooting and shoot_cooldown == 0:
                shot_dx = mouse_x - player_x
                shot_dy = mouse_y - player_y
                shot_distance = (shot_dx ** 2 + shot_dy ** 2) ** 0.5
                shot_dx /= shot_distance
                shot_dy /= shot_distance

                # Adiciona o tiro à lista de tiros
                shots.append((player_id, player_x, player_y, shot_dx, shot_dy))

                # Reinicia o tempo de recarga da arma
                shoot_cooldown = SHOOT_COOLDOWN

            # Atualiza a posição dos tiros
            updated_shots = []
            for shot_player_id, shot_x, shot_y, shot_dx, shot_dy in shots:
                # Atualiza a posição do tiro
                shot_x += shot_dx * SHOT_SPEED
                shot_y += shot_dy * SHOT_SPEED

                # Verifica se o tiro ainda está dentro da tela
                if 0 <= shot_x <= SCREEN_WIDTH and 0 <= shot_y <= SCREEN_HEIGHT:
                    updated_shots.append((shot_player_id, shot_x, shot_y, shot_dx, shot_dy))

            # Envia os dados atualizados para o cliente
            players[player_id] = (player_x, player_y)
            updated_shots = [(shot_x, shot_y) for _, shot_x, shot_y, _, _ in shots]

            # Adiciona as informações de game_over e winner ao objeto serializado
            data = pickle.dumps((players, updated_shots, game_over, winner))

            # Envia os dados para o cliente
            client_socket.send(data)

        except (EOFError, ConnectionResetError):
            break

    # Encerra a conexão com o jogador
    client_socket.close()
    del players[player_id]
    print('Conexão encerrada com o jogador', player_id)

# Função para atualizar a posição dos tiros
def update_shots():
    while True:
        updated_shots = []
        for shot_player_id, shot_x, shot_y, shot_dx, shot_dy in shots:
            # Atualiza a posição do tiro
            shot_x += shot_dx * SHOT_SPEED
            shot_y += shot_dy * SHOT_SPEED

            # Verifica se o tiro ainda está dentro da tela
            if 0 <= shot_x <= SCREEN_WIDTH and 0 <= shot_y <= SCREEN_HEIGHT:
                updated_shots.append((shot_player_id, shot_x, shot_y, shot_dx, shot_dy))
        shots[:] = updated_shots  # Atualiza a lista de tiros

        # Delay para controlar a velocidade de atualização dos tiros
        threading.Event().wait(0.01)

# Loop principal para lidar com as conexões dos clientes
player_id = 1

# Inicia a thread para atualizar os tiros
update_shots_thread = threading.Thread(target=update_shots)
update_shots_thread.start()

while True:
    # Aceita a conexão de um cliente
    client_socket, client_address = server_socket.accept()
    print('Conexão estabelecida com', client_address)

    # Armazena as informações do jogador conectado
    players[player_id] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Inicia uma nova thread para lidar com o jogador
    client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, player_id))
    client_thread.start()

    player_id += 1

# Encerra o servidor
server_socket.close()
print('Servidor encerrado.')