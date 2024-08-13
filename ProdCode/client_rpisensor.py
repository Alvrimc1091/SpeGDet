import socket

def send_file(conn, filename):
    with open(filename, 'rb') as f:
        print(f"Sending {filename}...")
        while True:
            data = f.read(1024)
            if not data:
                break
            conn.sendall(data)
    print(f"{filename} sent successfully.")

def main():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server
    server_ip = '192.168.2.30'  # Replace with the server's IP address
    server_port = 65432
    client_socket.connect((server_ip, server_port))
    
    # Send files
    send_file(client_socket, 'text_file.txt')
    send_file(client_socket, 'binary_file.bin')
    
    # Close the connection
    client_socket.close()

if __name__ == "__main__":
    main()
