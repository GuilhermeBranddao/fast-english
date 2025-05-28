# client.py (ou seu arquivo de jogo principal)
import pygame
from network import Network # Supondo que a classe Network esteja em network.py

# --- Constantes ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 30
FPS = 60

# --- Cores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Player:
    def __init__(self, x, y, player_id, color=RED):
        self.x = x
        self.y = y
        self.id = player_id
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = 5

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        # Mantém o jogador dentro da tela (exemplo simples)
        self.x = max(0, min(self.x, SCREEN_WIDTH - PLAYER_SIZE))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - PLAYER_SIZE))
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        # Opcional: Desenha o ID do jogador
        font = pygame.font.SysFont(None, 20)
        id_text = font.render(str(self.id), True, BLACK)
        screen.blit(id_text, (self.rect.x + 5, self.rect.y - 15))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jogo Multiplayer Simples")
    clock = pygame.time.Clock()

    # --- Rede ---
    network = Network(server_host='localhost') # Mude 'localhost' para o IP do servidor se estiver em outra máquina
    my_player_id = network.connect()

    if my_player_id is None:
        print("Não foi possível conectar ao servidor. Encerrando.")
        pygame.quit()
        return

    # --- Jogador Local e Outros Jogadores ---
    # O servidor define a posição inicial, mas podemos criar o objeto Player antes de receber o primeiro estado
    local_player = Player(50, 50, my_player_id, RED) # Cor pode ser atualizada pelo servidor
    other_players = {} # {player_id: Player_object}

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 # Delta time em segundos

        # --- Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Movimentação do Jogador Local ---
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        
        if dx != 0 or dy != 0:
            local_player.move(dx, dy)
            network.send_position(local_player.x, local_player.y)

        # --- Receber Estado do Jogo ---
        game_state = network.receive_game_state()
        
        if game_state == "NO_DATA" or game_state == "PARTIAL_DATA" or game_state == "NO_VALID_STATE":
            # Nenhuma nova atualização completa ainda, ou dados parciais
            pass # Continua com o último estado conhecido
        elif game_state is None: # Erro de conexão
            print("Conexão com o servidor perdida.")
            running = False
        elif isinstance(game_state, dict):
            # Atualizar posições dos jogadores
            current_player_ids_on_server = set(game_state.keys())

            # Adicionar/Atualizar jogadores existentes
            for p_id, data in game_state.items():
                if p_id == my_player_id:
                    # Atualiza o jogador local SE o servidor for a autoridade.
                    # Para este exemplo, o cliente move e envia, mas o servidor pode corrigir.
                    # Para simplificar, podemos deixar o cliente ser autoritativo sobre sua posição inicial
                    # e apenas usar o servidor para cor, ou aceitar a posição do servidor.
                    local_player.x = data['x']
                    local_player.y = data['y']
                    local_player.color = data['color']
                    local_player.rect.topleft = (local_player.x, local_player.y)
                else:
                    if p_id not in other_players:
                        other_players[p_id] = Player(data['x'], data['y'], p_id, data['color'])
                    else:
                        other_players[p_id].x = data['x']
                        other_players[p_id].y = data['y']
                        other_players[p_id].color = data['color']
                        other_players[p_id].rect.topleft = (other_players[p_id].x, other_players[p_id].y)
            
            # Remover jogadores que não estão mais no estado do servidor
            ids_to_remove = set(other_players.keys()) - current_player_ids_on_server
            for p_id_remove in ids_to_remove:
                if p_id_remove != my_player_id: # Não remove o jogador local daqui
                    del other_players[p_id_remove]


        # --- Desenhar ---
        screen.fill(WHITE)
        local_player.draw(screen)
        for p_id in list(other_players.keys()): # list() para evitar erro se other_players mudar
            if p_id in other_players: # Checagem extra caso um jogador seja removido por outra thread/lógica
                 other_players[p_id].draw(screen)
        pygame.display.flip()

    # --- Encerrar ---
    network.close()
    pygame.quit()

if __name__ == "__main__":
    main()