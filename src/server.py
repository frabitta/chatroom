from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# definizione delle costanti della connesisone (indirizzo e buffer)
HOST = ''
PORT = 53000
QUEUE = 5
BUFFSIZE = 1024
SERVER_NAME = "SERVER"
QUIT_COMMAND = "?{quit}"
ADDR = (HOST, PORT)

users = {}

# creazione del socket
def start_server(addr):
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(addr)
    server.listen(QUEUE)
    print("Server in ascolto...")

    while True:
        client_socket, client_address = server.accept()
        print("si è collegato ", client_address)
        Thread(target=client_manager, args=(client_socket,)).start()
    server.close()

def client_manager(client_socket):
    send_message(client_socket, SERVER_NAME, "Benvenuto! Digita il tuo nome")
    
    name = client_socket.recv(BUFFSIZE).decode("utf8")
    while name == SERVER_NAME:
        send_message(client_socket, SERVER_NAME, "Nome utente non valido, riprova")
        name = client_socket.recv(BUFFSIZE).decode("utf8")
    send_message_toAll(SERVER_NAME, name + " è entrato nella chat")
    users[client_socket] = name
    
    clientConnected = True
    while clientConnected:
        msg = client_socket.recv(BUFFSIZE).decode("utf8")

        if msg != QUIT_COMMAND:
            send_message_toAll(name, msg)
        else:
            client_socket.send(bytes(QUIT_COMMAND, "utf8"))
            client_socket.close()
            del users[client_socket]
            send_message_toAll(SERVER_NAME, name + " ha abbandonato la Chat.")
            break

def send_message_toAll(ori, msg):
    for client in users:
        send_message(client, ori, msg)

def send_message(dest, ori, msg):
    dest.send(bytes(ori + ": " + msg, "utf8"))

if __name__ == "__main__":
    start_server(ADDR)