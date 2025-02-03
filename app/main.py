import socket  # noqa: F401
import threading
import logging
import time


# Redis Parser
class RESPParser:
    def parse(self, data):

        """
        Parses RESP data based on the first byte.
        """

        if data.startswith(b"+"):
            return self._parse_simple_string(data)
        elif data.startswith(b"-"):
            return self._parse_error(data)
        elif data.startswith(b":"):
            return self._parse_integer(data)
        elif data.startswith(b"$"):
            return self._parse_bulk_string(data)
        elif data.startswith(b"*"):
            return self._parse_array(data)
        else:
            raise ValueError("Unknown RESP data type")
        
    def _parse_simple_string(self, data):
        return data[1:-2].decode()
    
    def _parse_error(self, data):
        return Exception(data[1:-2].decode())
    
    def _parse_integer(self, data):
        return int(data[1:-2])

    def _parse_bulk_string(self, data):
        lines = data.split(b"\r\n",2)
        length = int(lines[0][1:])
        if length == -1:
            return None
        return lines[1].decode()
    
    def _parse_array(self, data):
        lines = data.split(b"\r\n")
        num_elements = int(lines[0][1:])
        elements = []
        index = 1 
        for _ in range(num_elements):
            length = int(lines[index][1:])
            elements.append(lines[index + 1].decode())
            index += 2 
        return elements

def start_server():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Server is running on localhost:6379")
    return server_socket

def accept_connections(server_socket):
    while True:
        connection, addr = server_socket.accept()
        print(f"Connected by {addr}")
        client_thread = threading.Thread(target=handle_client, args=(connection, addr))
        client_thread.daemon = True
        client_thread.start()

def handle_client(connection, addr):
    try:
        while True:
            data = connection.recv(1024)
            if not data:
                print(f"client {addr} disconnected.")
                break
            parser = RESPParser()
            try:
                parsed_command = parser.parse(data)
                if len(parsed_command) > 1:
                    if parsed_command[0].upper() == "ECHO":
                        message = parsed_command[1]
                        response = f"${len(message)}\r\n{message}\r\n".encode()
                else:
                    if parsed_command[0].upper() == "PING":
                        response = b"+PONG\r\n"
                    else:
                        response = b"-ERR unknown command\r\n"
            except Exception as e:
                response = f"-ERR {str(e)}\r\n".encode()
    
            connection.sendall(response)

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        connection.close()
    

def main():
    server_socket = start_server()
    try:
        accept_connections(server_socket)
    except KeyboardInterrupt:
        print("Shutting down the server.")
    finally:
        server_socket.close()
    

if __name__ == "__main__":
    main()
