from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import ChatServer

HOST = 'asda'
PORT = ChatServer.PORT
BUFFSIZE = ChatServer.BUFFSIZE
QUIT_COMMAND = ChatServer.QUIT_COMMAND
ADDR = (HOST, PORT)

listeners = []

def receiver(client_socket):
    while True:
        try:
            msg = client_socket.recv(BUFFSIZE).decode("utf8")
            print(msg)
            notifyIncomingMsg(msg)
        except OSError:
            closeConnection(client_socket)
            break

def notifyIncomingMsg(msg):
    for listener in listeners:
        listener.updateMessages(msg)

def notifyClosedConnection():
    for listener in listeners:
        listener.closedConnection()

def addListener(listener):
    listeners.append(listener)

def connect(addr, name = "USR"):
    client_name = name
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect(ADDR)                      #----------------------------
    except Exception as data:
        print("Errore di connessione")
        print(data)
        closeConnection(client_socket)
    send_message(client_socket, client_name)
    Thread(target=receiver, args=(client_socket,)).start()
    return client_socket

def send_message(client_socket, msg):
    try:
        client_socket.send(bytes(msg, "utf8"))
    except OSError:
        closeConnection(client_socket)
    if msg == QUIT_COMMAND:
        closeConnection(client_socket)

def closeConnection(client_socket):
    client_socket.close()
    print("Connessione chiusa")
    notifyClosedConnection()

if __name__ == "__main__":
    connect(ADDR)
