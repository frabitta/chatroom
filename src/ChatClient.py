from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import ChatServer

# Definizione delle costanti di connessione
HOST = 'localhost'
PORT = ChatServer.PORT                      # da cambiare e non fare riferimento all'altro modulo???----------------
BUFFSIZE = ChatServer.BUFFSIZE
QUIT_COMMAND = ChatServer.QUIT_COMMAND
ADDR = (HOST, PORT)
# Definizione delle variabili globali: applicazione in ascolto e status del client
listener = None
statusActive = False

def receiver(client_socket):
    client_socket.settimeout(1.0)
    while statusActive:
        try:
            msg = client_socket.recv(BUFFSIZE).decode("utf8")
            notifyIncomingMsg(msg)
        except TimeoutError:
            continue
        except OSError:
            closeConnection(client_socket)
            break

def notifyIncomingMsg(msg):
    global listener
    listener.updateMessages(msg)

def notifyClosedConnection():
    global listener
    listener.closedConnection()

def addListener(new_listener):
    global listener
    listener = new_listener

def connect(addr, name = "USR"):
    global statusActive
    client_name = name
    client_socket = socket(AF_INET, SOCK_STREAM)
    thread = None
    try:
        client_socket.connect(ADDR)
        statusActive = True
        send_message(client_socket, client_name)
        thread = Thread(target=receiver, args=(client_socket,))
        thread.start()
    except Exception as data:
        print("Errore di connessione")
        closeConnection(client_socket)
    return thread, client_socket

def send_message(client_socket, msg):
    try:
        client_socket.send(bytes(msg, "utf8"))
    except OSError:
        closeConnection(client_socket)
    if msg == QUIT_COMMAND:
        closeConnection(client_socket)

def closeConnection(client_socket):
    global statusActive
    if statusActive:
        statusActive = False
        try:
            client_socket.close()
            print("Connessione chiusa")
        except OSError:                           # server????---------------------------------
            print("Errore nella chiusura della connessione (client già chiuso?)")
        notifyClosedConnection()

if __name__ == "__main__":
    connect(ADDR)
