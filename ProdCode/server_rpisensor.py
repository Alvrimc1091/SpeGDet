import socket

def receive_file(sock, filename):
    with open(filename, 'wb') as f:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            f.write(data)
    print(f"Received file: {filename}")

def main():
    host = '0.0.0.0'
    port = 8080

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server is listening...")

    while True:
        # Accept a connection
        conn, addr = server_socket.accept()
        print(f"Connected to {addr}")

        # Receive the file type
        file_type = conn.recv(1024).decode()
        if file_type not in ['type1', 'type2']:
            print("Unknown file type")
            conn.close()
            continue

        # Receive the filename
        filename = conn.recv(1024).decode()
        print(f"Receiving file: {filename}")

        receive_file(conn, filename)
        conn.close()

if __name__ == "__main__":
    main()
