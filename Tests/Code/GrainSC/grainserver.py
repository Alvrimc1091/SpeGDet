import socket
import threading
import time

class DataServer:
    def __init__(self):
        self.servers = {}
        self.connected_clients = []

    def add_server(self, port, data):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('192.168.3.101', port))
        self.servers[port] = {'server': server, 'data': data}

    def start_servers(self):
        for port, info in self.servers.items():
            server_thread = threading.Thread(target=self._serve_data, args=(info['server'], info['data']))
            server_thread.daemon = True
            server_thread.start()

    def _serve_data(self, server, data):
        server.listen(5)
        print(f"Server listening on {server.getsockname()}")

        while True:
            connection, _ = server.accept()
            print(f"Connection established from {connection.getpeername()}")
            self.connected_clients.append(connection)

            try:
                while True:
                    received_data = connection.recv(1024).decode()
                    print(f"Received command from {connection.getpeername()}: {received_data}")

                    # Si se recibe el comando "exit" o "q", enviar el comando a todos los clientes y salir
                    if received_data.lower() in ["exit", "q"]:
                        for client in self.connected_clients:
                            client.sendall(received_data.encode())
                        print("Exiting server...")
                        time.sleep(2)  # Espera 2 segundos antes de salir
                        exit()

                    # Envía datos periódicamente
                    connection.sendall(data.encode())
                    time.sleep(5)  # Envía datos cada 5 segundos
            except ConnectionResetError:
                print(f"Connection with {connection.getpeername()} closed.")
                self.connected_clients.remove(connection)
                connection.close()

if __name__ == "__main__":
    data_server = DataServer()

    # Agregar servidores con datos específicos en puertos específicos
    data_server.add_server(8080, "Dato 1")
    data_server.add_server(8081, "Dato 2")
    data_server.add_server(8082, "Dato 3")
    data_server.add_server(8083, "Dato 4")

    # Iniciar los servidores en hilos separados
    data_server.start_servers()

    # Entrada para manejar comandos desde la terminal del servidor
    while True:
        command = input("Enter command: ")
        if command.lower() in ["exit", "q"]:
            print("Exiting server...")
            for client in data_server.connected_clients:
                client.sendall(command.encode())
            time.sleep(2)  # Espera 2 segundos antes de salir
            exit()
        else:
            print("Unknown command.")
