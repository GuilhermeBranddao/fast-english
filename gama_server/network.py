# network.py (ou parte do seu arquivo de jogo principal)
import socket

class Network:
    def __init__(self, server_host='localhost', server_port=12345):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (server_host, server_port)
        self.player_id = None
        self.buffer = "" # Para lidar com mensagens parciais

    def connect(self):
        """Tenta conectar ao servidor e obter o ID do jogador."""
        try:
            self.client_socket.connect(self.server_address)
            # Espera a mensagem de ID do servidor
            # Formato esperado: "ID,<player_id>"
            initial_message = self.client_socket.recv(1024).decode('utf-8')
            parts = initial_message.split(',')
            if parts[0] == 'ID' and len(parts) == 2:
                self.player_id = int(parts[1])
                print(f"Conectado ao servidor. Meu ID: {self.player_id}")
                return self.player_id
            else:
                print(f"Falha ao obter ID do servidor. Mensagem: {initial_message}")
                self.close()
                return None
        except socket.error as e:
            print(f"Erro de conexão: {e}")
            return None
        except ValueError:
            print(f"ID recebido do servidor não é um número válido: {initial_message}")
            self.close()
            return None

    def send_position(self, x, y):
        """Envia a posição (x, y) do jogador para o servidor."""
        if self.player_id is None:
            print("Não conectado, não é possível enviar posição.")
            return False
        try:
            message = f"UPDATE,{int(x)},{int(y)}"
            self.client_socket.sendall(message.encode('utf-8'))
            return True
        except socket.error as e:
            print(f"Erro ao enviar posição: {e}")
            # Em um jogo real, você pode tentar reconectar ou tratar o erro de forma mais robusta
            self.close() # Fecha a conexão em caso de erro grave de envio
            return False

    def receive_game_state(self):
        """
        Recebe o estado do jogo do servidor.
        Retorna um dicionário com os dados dos jogadores ou None em caso de erro.
        Ex: {player_id: {'x': x, 'y': y, 'color': (r,g,b)}, ...}
        """
        try:
            # Adiciona novos dados ao buffer
            self.buffer += self.client_socket.recv(4096).decode('utf-8')
        except socket.error as e:
            print(f"Erro ao receber dados: {e}")
            self.close() # Fecha a conexão em caso de erro grave de recepção
            return None
        except BlockingIOError: # Se o socket estiver em modo não bloqueante
            return "NO_DATA" # Ou algum indicador de que não há dados agora

        # Processa mensagens completas no buffer
        # Mensagens são separadas por algum delimitador implícito ou tamanho fixo
        # Aqui, estamos assumindo que cada recv() pode conter múltiplas mensagens "STATE;..."
        # ou partes dela. A forma mais robusta é garantir que o servidor envie mensagens
        # com um delimitador claro ou prefixo de tamanho.
        # Para este exemplo, vamos assumir que uma mensagem "STATE;" é a última e completa.
        
        if "STATE;" not in self.buffer:
            return "PARTIAL_DATA" # Ainda não recebeu uma mensagem de estado completa

        # Pega a última mensagem de estado completa
        # Isso é uma simplificação. Um parser mais robusto é necessário para produção.
        messages = self.buffer.split("STATE;")
        last_complete_state_str = ""
        if len(messages) > 1 :
            # A última mensagem pode estar incompleta, então pegamos a penúltima parte que segue um "STATE;"
            # ou a última se ela não for vazia e a anterior for "STATE;"
            for i in range(len(messages) -1, 0, -1):
                if messages[i]: # Se a parte após STATE; não for vazia
                    last_complete_state_str = messages[i]
                    break
            # Atualiza o buffer com o que sobrou (pode ser uma mensagem parcial)
            self.buffer = messages[-1] if messages[-1] and "STATE;" not in messages[-1] else ""
        else: # Não encontrou "STATE;" ou só tem uma parte parcial
            return "PARTIAL_DATA"

        if not last_complete_state_str:
            return "NO_VALID_STATE"

        # Formato esperado: "id1,x1,y1,r1,g1,b1;id2,x2,y2,r2,g2,b2;..."
        players_data = {}
        player_entries = last_complete_state_str.strip().split(';')
        
        for entry in player_entries:
            if not entry: continue
            parts = entry.split(',')
            if len(parts) == 5: # id, x, y, r, g, b
                try:
                    p_id = int(parts[0])
                    x = int(parts[1])
                    y = int(parts[2])
                    color = (int(parts[3]), int(parts[4]), int(parts[5])) # Ajuste para RGB
                    players_data[p_id] = {'x': x, 'y': y, 'color': color}
                except ValueError:
                    print(f"Erro ao parsear dados do jogador: {entry}")
                    continue # Pula esta entrada mal formada
            elif len(parts) == 6: # id, x, y, r, g, b
                 try:
                    p_id = int(parts[0])
                    x = int(parts[1])
                    y = int(parts[2])
                    color = (int(parts[3]), int(parts[4]), int(parts[5]))
                    players_data[p_id] = {'x': x, 'y': y, 'color': color}
                 except ValueError:
                    print(f"Erro ao parsear dados do jogador (6 partes): {entry}")
                    continue
            else:
                print(f"Entrada de jogador mal formatada (número incorreto de partes {len(parts)}): '{entry}' na string '{last_complete_state_str}'")


        return players_data

    def close(self):
        """Fecha a conexão do socket."""
        print("Fechando conexão com o servidor.")
        self.client_socket.close()
        self.player_id = None