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
ADDR = (HOST, PORT)

users = {}

# creazione del socket
def start_server(addr):
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(addr)
    server.listen(QUEUE)
    print("Server in ascolto sulla porta", addr[1])
    Thread(target=accept_connections, args=(server,)).start()

def accept_connections(server):
    active = True
    while active:
        client_socket, client_address = server.accept()
        print("si è collegato ", client_address)
        Thread(target=client_manager, args=(client_socket,)).start()
        if users.__len__ == 0:
            active = False
    server.close()
    print("Server chiuso")

def client_manager(client_socket):
    send_message(client_socket, SERVER_NAME, "Benvenuto! Digita il tuo nome")
    
    name = client_socket.recv(BUFFSIZE).decode("utf8")
    if name == SERVER_NAME:
        name = DEFAULT_USER_NAME
    new_name = name
    i = 1
    while new_name in users.values():
        new_name = name + "_" + str(i)
        i += 1
    name = new_name

    send_message_toAll(SERVER_NAME, name + " è entrato nella chat")
    users[client_socket] = name
    
    clientConnected = True
    while clientConnected:
        msg = client_socket.recv(BUFFSIZE).decode("utf8")

        if msg != QUIT_COMMAND:
            send_message_toAll(name, msg)
        else:
            client_socket.close()
            del users[client_socket]
            print(name + " ha abbandonato la Chat.")
            send_message_toAll(SERVER_NAME, name + " ha abbandonato la Chat.")
            clientConnected = False

def send_message_toAll(ori, msg):
    for client in users:
        send_message(client, ori, msg)

def send_message(dest, ori, msg):
    dest.send(bytes(ori + ": " + msg, "utf8"))

if __name__ == "__main__":
    start_server(ADDR)