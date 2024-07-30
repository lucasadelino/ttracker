import socket
import sys

# Define the socket file path
SOCKET_FILE = f"/tmp/ttracker_{sys.argv[1]}"

# Create a Unix domain socket
client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect the socket to the file path where the server is listening
client_socket.connect(SOCKET_FILE)

try:
    # Send data to the server
    message = sys.argv[2]
    print(f"Sending message: {message}")
    client_socket.sendall(message.encode())
finally:
    # Clean up the socket
    client_socket.close()
