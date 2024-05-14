from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# definizione delle costanti della connesisone (indirizzo e buffer)
HOST = 'localhost'
PORT = 53000
QUEUE = 5
BUFFSIZE = 1024
QUIT_COMMAND = "?{quit}"
ADDR = (HOST, PORT)

def receiver(my_socket):
    while True:
        try:
            msg = my_socket.recv(BUFFSIZE).decode("utf8")
            print(msg)
        except OSError:
            break

def connect(addr):
    my_socket = socket(AF_INET, SOCK_STREAM)
    my_socket.connect(ADDR)
    Thread(target=receiver, args=(my_socket,)).start()

if __name__ == "__main__":
    connect(ADDR)
