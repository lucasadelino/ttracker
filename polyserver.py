import os
import socket


class Server:
    def __init__(self, socket_name) -> None:
        # Define the socket file path
        SOCKET_FILE = f"/tmp/ttracker_{socket_name}"

        # Ensure the socket file does not already exist
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)

        # Create a Unix domain socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Bind the socket to the file path
        self.server_socket.bind(SOCKET_FILE)

        self.server_socket.listen(1)

    def listen(self):
        # Listen for incoming connections
        try:
            # Accept a connection
            client_connection, _ = self.server_socket.accept()
            # Read data from the client
            data = client_connection.recv(1024)
            if data:
                return data.decode()
        except:
            return None
        finally:
            client_connection.close()
