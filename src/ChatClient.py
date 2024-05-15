from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import ChatServer

# Definizione delle costanti di connessione
HOST = 'localhost'
PORT = ChatServer.PORT
BUFFSIZE = ChatServer.BUFFSIZE
QUIT_COMMAND = ChatServer.QUIT_COMMAND
ADDR = (HOST, PORT)
# Definizione delle variabili globali: applicazione in ascolto e status del client
listener = None
statusActive = False

def connect(addr, name = "USR"):
    """
    Avvia la connessione al server sulla porta (addr) specificata
    """
    global statusActive
    # creazione del socket
    client_name = name
    client_socket = socket(AF_INET, SOCK_STREAM)
    thread = None
    # tentativo di coneessione al server, se fallisce annulliamo tutto
    try:
        client_socket.connect(addr)
        statusActive = True
        # invio del nome utente al server
        send_message(client_socket, client_name)
        # avvio del thread di ascolto dei messaggi
        thread = Thread(target=receiver, args=(client_socket,))
        thread.start()
    except Exception as data:
        print("Errore di connessione")
        closeConnection(client_socket)
    return thread, client_socket

def closeConnection(client_socket):
    """
    Chiude la connessione con il server del socket client_socket
    """
    global statusActive
    # Terminiamo solo se risulta essere ancora attivo
    if statusActive:
        statusActive = False
        # -------------------------------------------------------------------------------------
        try:
            client_socket.close()
            print("Connessione chiusa")
        except OSError:                           # server????---------------------------------
            print("Errore nella chiusura della connessione (client già chiuso?)")
        notifyClosedConnection()

def receiver(client_socket):
    """
    Ascolta e riceve i messaggi dal server sul socket client_socket
    """
    # Usiamo il timeout per far si che non resti bloccato in attesa di ricevere messaggi
    # se il socket viene chiuso statusActive viene posto a False, terminando il ciclo e il thread
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

def send_message(client_socket, msg):
    """
    Invio di un messaggio (msg) al server tramite client_socket
    """
    # In caso di errore o di messaggio corrispondente al comando di uscita terminiamo la connessione
    try:
        client_socket.send(bytes(msg, "utf8"))
    except OSError:
        closeConnection(client_socket)
    if msg == QUIT_COMMAND:
        closeConnection(client_socket)

def addListener(new_listener):
    """
    Imposta l'applicazione che ascolta i messagi in ricezione
    """
    global listener
    listener = new_listener

def notifyIncomingMsg(msg):
    """
    Notifica l'applicazione dell'arrivo di un nuovo messaggio
    """
    global listener
    if listener is not None:
        listener.updateMessages(msg)
    else:
        print(msg)

def notifyClosedConnection():
    """
    Notifica l'applicazione della chiusura della connessione col server
    """
    global listener
    if listener is not None:
        listener.closedConnection()
    else:
        print("Connessione chiusa")

# Se lanciato come script, avvia il client come solo "ascoltatore"
if __name__ == "__main__":
    connect(ADDR)
