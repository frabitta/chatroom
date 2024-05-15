from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# Definizione delle costanti della connessione
HOST = ''
PORT = 53000
QUEUE = 5
BUFFSIZE = 1024
SERVER_NAME = "SERVER"
DEFAULT_USER_NAME = "USR"
QUIT_COMMAND = "?{quit}"
TIMEOUT = 10.0
ADDR = (HOST, PORT)
# Dizionari dei client connessi: socket -> nome utente, socket -> indirizzo
users = {}
addresses = {}
# Definizione delle variabili globali: thread di accettaione delle connessioni, socket del server, stato del server
acceptThread = None
server_socket = None
server_activeStatus = False

def start_server(addr):
    """
    Avvia il server sulla porta (addr) specificata
    """
    global server_socket
    global acceptThread
    global server_activeStatus
    # creazione del socket
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(addr)
    server_socket.listen(QUEUE)
    server_activeStatus = True
    print("Server in ascolto sulla porta", addr[1])
    # avvio del thread per accettare le richieste di connessione
    acceptThread = Thread(target=accept_connections)
    acceptThread.start()

def closeServer():
    """
    Chiude il server
    """
    global server_socket
    global acceptThread
    global server_activeStatus
    if server_activeStatus:
        server_activeStatus = False
        # chiudo tutti i socket dei client connessi                     ------------------------------
        # attendo la chiusura di tutti i thread di gestione dei client  ------------------------------
        # chiusura del socket del server e del thread di accettazione
        server_socket.close()
        acceptThread.join()
        print("Server chiuso")

def accept_connections():
    """
    Accetta le richieste di connessione e avvia un thread per la gestione di ogni client connesso
    (Da lanciare come Thread indipendente)
    """
    # Finchè il server è "attivo", accetto le richieste di connessione
    while server_activeStatus:
        # Attendo una richiesta di connessione e la soddisfo,
        # nel caso di errore (socket server non disponibile) continuo il ciclo (active sarà False)
        try:
            client_socket, client_address = server_socket.accept()
            # Aggiungo l'indirizzo alla lista degli utenti
            addresses[client_socket] = client_address
            print("Si è collegato ", client_address)
            # Avvio il thread di gestione del client
            Thread(target=client_manager, args=(client_socket,)).start()
        except OSError:
            continue

def client_manager(client_socket):
    """
    Gestisce la connessione con un client (client_socket)
        - riceve messaggi e li invia a tutti i client connessi
        - gestisce richiesta e casi di disconnessione
    """
    send_message(client_socket, SERVER_NAME, "Benvenuto! Inizia a chattare inviando il tuo primo messaggio!")
    # Impostiamo l'username, se non riceviamo un nome entro il limite di tempo, assegnamo un nome di default
    client_socket.settimeout(TIMEOUT)
    try:
        name = client_socket.recv(BUFFSIZE).decode("utf8")
    except TimeoutError:
        name = DEFAULT_USER_NAME
    if name == SERVER_NAME:
        name = DEFAULT_USER_NAME
    new_name = name
    i = 1
    while new_name in users.values():
        new_name = name + "_" + str(i)
        i += 1
    name = new_name
    # Mandiamo la notifica di ingresso nella chat
    send_message_toAll(SERVER_NAME, name + " è entrato nella chat")
    # Aggiungo il nome utente alla lista degli utenti
    users[client_socket] = name
    # Gestisco la chat finchè il client è connesso
    while client_socket in users:
        client_socket.settimeout(1.0)
        # Se incontro un errore nella connessione (client disconnesso), chiudo la connessione
        try:
            # Se riceviamo un messaggio, lo inviamo a tutti gli utenti, a meno che non sia un comando di uscita
            msg = client_socket.recv(BUFFSIZE).decode("utf8")
            if msg != QUIT_COMMAND:
                send_message_toAll(name, msg)
            else:
                closeConnection(client_socket)
        # Questo è necessario per non restare bloccati nella funzione recv (es. se l'utente si disconnette senza inviare un messaggio)
        except TimeoutError:
            continue
        except OSError:
            closeConnection(client_socket)
            continue

def closeConnection(client_socket):
    """
    Chiude la connessione con il client e notifica la disconnessione a tutti gli altri utenti
    """
    name = users[client_socket]
    client_socket.close()
    print(addresses[client_socket], " si è disconnesso.")
    del users[client_socket]
    del addresses[client_socket]
    send_message_toAll(SERVER_NAME, name + " ha abbandonato la Chat.")
    # Se non ci sono più utenti connessi, chiudo il server
    if len(users) == 0:
        closeServer()

def send_message_toAll(ori, msg):
    """
    Invia un messaggio a tutti gli utenti connessi
    """
    for client in users:
        send_message(client, ori, msg)

def send_message(dest, ori, msg):
    """
    Invia un messaggio al destinatario (dest: socket) con il mittente (ori: string) e messaggio (msg: string)
    """
    try:
        dest.send(bytes(ori + ": " + msg, "utf8"))
    # Se il destinatario non è più connesso, chiudo la connessione
    except OSError:
        closeConnection(dest)

# Se lanciato come script, avvia il server
if __name__ == "__main__":
    start_server(ADDR)