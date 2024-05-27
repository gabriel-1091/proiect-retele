import sys
import socket
import threading

SERVER_ADDRESSES = [("127.0.0.1", 3333), ("127.0.0.1", 3334), ("127.0.0.1", 3335)]


def handle_server_messages(s):
    while True:
        try:
            data = s.recv(1024).decode()
            if not data:
                break
            if data.startswith("load_update"):
                clients.notify_all(data)
            if data == "server_shutdown":
                print("Server is shutting down. Closing connection.")
                break
            print(data)
        except Exception as e:
            if str(e) != "[WinError 10053] An established connection was aborted by the software in your host machine":
                print(f"Error receiving data from server: {e}")
            break
    s.close()

def connect_to_server(server_addresses):
    for server in server_addresses:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(server)
            response = s.recv(1024).decode()
            if response == 'server_full':
                print(f"Server {server} is full. Trying next server...")
                s.close()
                continue
            print(f"Connected to server {server}")
            return s
        except Exception as e:
            print(f"Failed to connect to server {server}: {e}")
    return None


class ClientList:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()

    def add_client(self, client, addr):
        with self.lock:
            if len(self.clients) < 2:  # Limit to 2 clients
                self.clients.append((client, addr))
                return True
            else:
                return False

    def remove_client(self, client):
        with self.lock:
            self.clients = [c for c in self.clients if c[0] != client]

    def notify_all(self, message, sender=None):
        with self.lock:
            for client, addr in self.clients:
                if client != sender:
                    try:
                        client.sendall(message.encode())
                    except:
                        self.clients.remove((client, addr))

clients = ClientList()
is_running = True

def execute_method(num_threads, method_name, client_socket, args):
    threads = []
    def target_method(args, results):
        method = getattr(SomeClass(), method_name, None)
        if method:
            result = method(*args)
            results.append(result)

    results = []
    increment_load(int(num_threads))
    for _ in range(int(num_threads)):
        t = threading.Thread(target=target_method, args=(args, results))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    decrement_load(int(num_threads))
    
    client_socket.sendall(str(results[0]).encode())

load = 0
load_lock = threading.Lock()

def increment_load(num_threads=1):
    global load
    with load_lock:
        load += num_threads
    notify_all_load_update()

def decrement_load(num_threads=1):
    global load
    with load_lock:
        load -= num_threads
    notify_all_load_update()

def notify_all_load_update():
    global load
    clients.notify_all(f"load_update {load}")

class SomeClass:
    def some_method(self, a, b):
        return a + b

def handle_client(client_socket, addr):
    try:
        print(f"\nClient {addr} connected.")
        clients.notify_all(f"New client connected: {addr} has joined the server", sender=client_socket)
        client_socket.sendall(f"You are now connected to the server at {addr}".encode())

        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            elif data.startswith("port_listening"):
                print(data)
            elif data == 'client_disconnected':
                clients.remove_client(client_socket)
                clients.notify_all(f"{addr} has disconnected from the server")
                print(f"{addr} has disconnected from the server")
                break
            elif data.startswith("execute_method"):
                data = data.split()
                num_threads = int(data[1])
                method_name = data[2]
                args = list(map(int, data[3:]))  # assuming args are integers
                execute_method(num_threads, method_name, client_socket, args)
            elif data == "get_load":
                current_load = load
                port = addr[1]
                client_socket.sendall(f"Current load on port {port}: {current_load}".encode())
            else:
                print(f"Message from the client: {data}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def accept_connections(server_socket):
    server_socket.settimeout(1.0)  # Set a timeout for the accept call
    while is_running:
        try:
            client_socket, addr = server_socket.accept()
            if clients.add_client(client_socket, addr):
                client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
                client_thread.start()
            else:
                client_socket.sendall(b'server_full')
                client_socket.close()
        except socket.timeout:
            continue
        except OSError as e:
            if is_running:
                print(f"Error accepting connections: {e}")
            break

def main(port):
    global is_running
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("127.0.0.1", port))
        server_socket.listen()
        print(f"Server listening on port {port}")
        accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
        accept_thread.start()

        if port not in [3333, 3334, 3335]:
            p_connection = input("Connect to server(0 for default): ")
            if p_connection == '0':
                server_socket = connect_to_server(SERVER_ADDRESSES)
            else:
                server_socket = connect_to_server([("127.0.0.1", int(p_connection))])
            
            if server_socket:
                server_thread = threading.Thread(target=handle_server_messages, args=(server_socket,))
                server_thread.start()
                server_socket.send(f"port_listening {port}".encode())
            else:
                print("Failed to connect to any server (all servers are at full capacity).")

        while True:
            message0 = input("Send the message to: (0 - server, 1 - clients, or exit): ")
            if message0 == '0':
                line = input('>')
                server_socket.send(line.encode())
            elif message0 == '1':
                message = input("\nEnter message to send to clients: ")
                clients.notify_all(f"\nMessage from server: {message}")
            elif message0 == 'exit':
                clients.notify_all('\nServer is shutting down')
                is_running = False
                try:
                    server_socket.send(b"client_disconnected")
                except:
                    pass
                break
    except BaseException as err:
        print(f"Error: {err}")
    finally:
        if server_socket:
            server_socket.close()
        accept_thread.join()  # Ensure the accept_connections thread exits

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <port>")
        sys.exit(1)
    main(int(sys.argv[1]))