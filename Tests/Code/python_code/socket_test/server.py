import socket
import threading
import time

class ConnectionHandler(threading.Thread):
    def __init__(self, client_socket, address):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.connected = True

    def run(self):
        print(f"Conexión establecida con {self.address}")
        while self.connected:
            try:
                data = self.client_socket.recv(1024)
                if data:
                    command = data.decode().strip()
                    print(f"Comando recibido desde {self.address}: {command}")
                    response = self.process_command(command)
                    self.client_socket.sendall(response.encode())
                else:
                    self.connected = False
            except Exception as e:
                print(f"Error al recibir datos de {self.address}: {e}")
                self.connected = False
        print(f"Conexión con {self.address} cerrada")
        self.client_socket.close()

    def process_command(self, command):
        if self.client_socket.getsockname()[1] == 5000:
            return "data2"
        elif self.client_socket.getsockname()[1] == 6000:
            return "foto2"
        else:
            return "Comando no reconocido"

class MultiPortServer:
    def __init__(self, ports):
        self.ports = ports
        self.server_sockets = []

    def start(self):
        for port in self.ports:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('192.168.3.101', port))
            server_socket.listen(5)
            self.server_sockets.append(server_socket)
            print(f"Servidor escuchando en el puerto {port}")

        # Iniciar el envío de "foto2" y "data2" cada 3 segundos
        threading.Thread(target=self.send_data_continuously).start()

        self.accept_connections()

    def accept_connections(self):
        while True:
            for server_socket in self.server_sockets:
                client_socket, address = server_socket.accept()
                handler = ConnectionHandler(client_socket, address)
                handler.start()

    def send_data_continuously(self):
        while True:
            for server_socket in self.server_sockets:
                client_socket, _ = server_socket.accept()
                port = client_socket.getsockname()[1]
                if port == 5000:
                    data = "data2"
                elif port == 6000:
                    data = "foto2"
                else:
                    data = "Comando no reconocido"
                client_socket.sendall(data.encode())
                client_socket.close()
            time.sleep(3)

if __name__ == "__main__":
    ports = [5000, 6000]
    server = MultiPortServer(ports)
    server.start()
