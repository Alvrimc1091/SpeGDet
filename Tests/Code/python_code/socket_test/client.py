import socket
import time

class SocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_command(self, command):
        try:
            print(f"Intentando conectarse a {self.host}:{self.port}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))
                client_socket.sendall(command.encode())
                response = client_socket.recv(1024)
                print(f"Respuesta del servidor: {response.decode()}")
        except Exception as e:
            print(f"Error al conectar al servidor: {e}")

if __name__ == "__main__":
    host = '192.168.3.101'
    # Crear instancias del cliente para cada puerto
    client_5000 = SocketClient('192.168.3.101', 5000)
    client_6000 = SocketClient('192.168.3.101', 6000)

    # Bucle infinito para enviar comandos cada 10 segundos
    while True:
        client_5000.send_command("test1")
        client_6000.send_command("foto1")
        time.sleep(10)
