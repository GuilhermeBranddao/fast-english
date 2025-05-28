# server.py
import socket
import threading
import time

class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar o endereço
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        
        self.clients = {}  # {client_socket: player_id}
        self.player_data = {}  # {player_id: {'x': int, 'y': int, 'color': tuple}}
        self.next_player_id = 0
        self.lock = threading.Lock() # Para proteger o acesso a dados compartilhados
        
        print(f"Servidor escutando em {host}:{port}")

    def get_random_color(self):
        # Gera uma cor aleatória simples para diferenciar jogadores
        import random
        return (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))

    def broadcast_state(self):
        """Envia o estado atual de todos os jogadores para todos os clientes."""
        with self.lock:
            if not self.player_data:
                return
            
            # Formato: "STATE;id1,x1,y1,r1,g1,b1;id2,x2,y2,r2,g2,b2;..."
            state_parts = []
            for player_id, data in self.player_data.items():
                color_str = ",".join(map(str, data['color']))
                state_parts.append(f"{player_id},{data['x']},{data['y']},{color_str}")
            
            message = "STATE;" + ";".join(state_parts)
            
            for client_socket in list(self.clients.keys()): # list() para evitar problemas ao remover
                try:
                    client_socket.sendall(message.encode('utf-8'))
                except socket.error as e:
                    print(f"Erro ao enviar para {self.clients.get(client_socket, 'desconhecido')}: {e}")
                    self.remove_client(client_socket)

    def remove_client(self, client_socket):
        with self.lock:
            player_id = self.clients.pop(client_socket, None)
            if player_id is not None:
                self.player_data.pop(player_id, None)
                print(f"Jogador {player_id} desconectado.")
            try:
                client_socket.close()
            except socket.error:
                pass # Socket pode já estar fechado

    def handle_client(self, client_socket, client_address):
        player_id = -1 # Inicializa com valor inválido
        try:
            with self.lock:
                player_id = self.next_player_id
                self.next_player_id += 1
                self.clients[client_socket] = player_id
                # Posição inicial e cor aleatória
                self.player_data[player_id] = {'x': 50, 'y': 50, 'color': self.get_random_color()} 
            
            print(f"Jogador {player_id} conectado de {client_address}")
            client_socket.sendall(f"ID,{player_id}".encode('utf-8')) # Envia o ID para o cliente

            self.broadcast_state() # Envia o estado inicial para todos

            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    print(f"Jogador {player_id} ({client_address}) enviou mensagem vazia. Desconectando.")
                    break # Conexão fechada pelo cliente

                # Lógica para processar a mensagem do cliente
                # Formato esperado: "UPDATE,x,y"
                parts = message.split(',')
                if parts[0] == 'UPDATE' and len(parts) == 3:
                    try:
                        x, y = int(parts[1]), int(parts[2])
                        with self.lock:
                            if player_id in self.player_data:
                                self.player_data[player_id]['x'] = x
                                self.player_data[player_id]['y'] = y
                        
                        # Não é estritamente necessário transmitir a cada movimento individual
                        # pode ser feito em um loop separado (veja broadcast_loop abaixo)
                        # self.broadcast_state()
                    except ValueError:
                        print(f"Jogador {player_id}: Mensagem mal formatada - {message}")
                else:
                    print(f"Jogador {player_id}: Comando desconhecido - {message}")

        except socket.error as e:
            print(f"Erro de socket com jogador {player_id} ({client_address}): {e}")
        except Exception as e:
            print(f"Erro inesperado com jogador {player_id} ({client_address}): {e}")
        finally:
            print(f"Fechando conexão com jogador {player_id} ({client_address}).")
            self.remove_client(client_socket)
            self.broadcast_state() # Informa aos outros que o jogador saiu

    def broadcast_loop(self, interval=1/30): # Transmite ~30 vezes por segundo
        """Loop separado para transmitir o estado do jogo."""
        while True:
            self.broadcast_state()
            time.sleep(interval)

    def start(self):
        # Inicia a thread de broadcast
        broadcast_thread = threading.Thread(target=self.broadcast_loop, daemon=True)
        broadcast_thread.start()

        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True)
                client_handler.start()
            except KeyboardInterrupt:
                print("Servidor encerrando...")
                break
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")
        
        for sock in self.clients.keys():
            sock.close()
        self.server_socket.close()
        print("Servidor encerrado.")


if __name__ == "__main__":
    server = GameServer()
    server.start()