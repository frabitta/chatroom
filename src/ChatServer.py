from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# definizione delle costanti della connesisone (indirizzo e buffer)
HOST = ''
PORT = 53000
QUEUE = 5
BUFFSIZE = 1024
SERVER_NAME = "SERVER"
DEFAULT_USER_NAME = "USR"
QUIT_COMMAND = "?{quit}"
TIMEOUT = 10.0
ADDR = (HOST, PORT)

users = {}
addresses = {}

acceptThread = None
server = None

def start_server(addr):
    global server
    global acceptThread
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(addr)
    server.listen(QUEUE)
    print("Server in ascolto sulla porta", addr[1])
    acceptThread = Thread(target=accept_connections, args=(server,))
    acceptThread.start()

active = True
def accept_connections(server):
    while active:
        try:
            client_socket, client_address = server.accept()
        except OSError:
            continue
        addresses[client_socket] = client_address
        print("si è collegato ", client_address)
        Thread(target=client_manager, args=(client_socket,)).start()

def closeServer():
    global server
    global acceptThread
    global active
    active = False
    server.close()
    acceptThread.join()
    print("Server chiuso")

def client_manager(client_socket):
    send_message(client_socket, SERVER_NAME, "Benvenuto! Inizia a chattare.")
    # Establishing the user's name
    # If the user doesn't send a name in the time limit, we assign a default one
    client_socket.settimeout(TIMEOUT)
    try:
        name = client_socket.recv(BUFFSIZE).decode("utf8")
    except TimeoutError:
        name = DEFAULT_USER_NAME
        return
    if name == SERVER_NAME:
        name = DEFAULT_USER_NAME
    new_name = name
    i = 1
    while new_name in users.values():
        new_name = name + "_" + str(i)
        i += 1
    name = new_name
    # Sending the welcome message
    send_message_toAll(SERVER_NAME, name + " è entrato nella chat")
    users[client_socket] = name
    # Managing the chat
    while client_socket in users:
        client_socket.settimeout(1.0)
        try:
            msg = client_socket.recv(BUFFSIZE).decode("utf8")
            if msg != QUIT_COMMAND:
                send_message_toAll(name, msg)
            else:
                closeConnection(client_socket)
        except TimeoutError:
            continue
        except OSError:
            closeConnection(client_socket)
            continue
    

def closeConnection(client_socket):
    name = users[client_socket]
    client_socket.close()
    print(addresses[client_socket], " si è disconnesso.")
    del users[client_socket]
    del addresses[client_socket]
    send_message_toAll(SERVER_NAME, name + " ha abbandonato la Chat.")
    if len(users) == 0:
        closeServer()

def send_message_toAll(ori, msg):
    for client in users:
        send_message(client, ori, msg)

def send_message(dest, ori, msg):
    # If we encounter an error, we close the connection with the client
    try:
        dest.send(bytes(ori + ": " + msg, "utf8"))
    except OSError:
        closeConnection(dest)

if __name__ == "__main__":
    start_server(ADDR)