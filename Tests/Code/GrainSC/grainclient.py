import socket
import threading

class DataClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_address, self.server_port))
            print(f"Connected to server at {self.server_address}:{self.server_port}")
            self.receive_data()
        except ConnectionRefusedError:
            print(f"Connection to server at {self.server_address}:{self.server_port} refused.")

    def receive_data(self):
        try:
            while True:
                data = self.client_socket.recv(1024).decode()
                print(f"Received data from server at {self.server_address}:{self.server_port}: {data}")
        except ConnectionResetError:
            print(f"Connection to server at {self.server_address}:{self.server_port} closed.")

if __name__ == "__main__":
    host = '192.168.3.101'

    # Crear instancias de clientes para cada servidor
    client_8080 = DataClient(host, 8080)
    client_8081 = DataClient(host, 8081)
    client_8082 = DataClient(host, 8082)
    client_8083 = DataClient(host, 8083)

    # Conectar a cada servidor en hilos separados
    threading.Thread(target=client_8080.connect_to_server).start()
    threading.Thread(target=client_8081.connect_to_server).start()
    threading.Thread(target=client_8082.connect_to_server).start()
    threading.Thread(target=client_8083.connect_to_server).start()
