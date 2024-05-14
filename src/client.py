from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# definizione delle costanti della connesisone (indirizzo e buffer)
HOST = 'localhost'
PORT = 53000
QUEUE = 5
BUFFSIZE = 1024
QUIT_COMMAND = "?{quit}"
ADDR = (HOST, PORT)

client_name = "USR1"

def receiver(client_socket):
    while True:
        try:
            msg = client_socket.recv(BUFFSIZE).decode("utf8")
            print(msg)
        except OSError:
            break

def connect(addr, name = "USR"):
    client_name = name
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
    client_socket.send(bytes(client_name, "utf8"))
    Thread(target=receiver, args=(client_socket,)).start()
    return client_socket

def send_message(client_socket, msg):
    client_socket.send(bytes(msg, "utf8"))
    if msg == QUIT_COMMAND:
        client_socket.close()
        print("Connessione chiusa")
        exit()

if __name__ == "__main__":
    connect(ADDR)
