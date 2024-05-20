from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys, signal, time
import ChatServer

# Definizione delle costanti di connessione
HOST = 'localhost'
PORT = ChatServer.PORT
BUFFSIZE = ChatServer.BUFFSIZE
QUIT_COMMAND = ChatServer.QUIT_COMMAND
ADDR = (HOST, PORT)
DEFAULT_USER_NAME = "USR"
# Definizione delle variabili globali: applicazione in ascolto e status del client
listener = None
statusActive = False
client_socket = None

def connect(addr = ADDR, name = DEFAULT_USER_NAME):
    """
    Avvia la connessione al server sulla porta (addr) specificata
    """
    global statusActive
    global client_socket
    # creazione del socket
    if name == "":
        name = DEFAULT_USER_NAME
    client_name = name
    client_socket = socket(AF_INET, SOCK_STREAM)
    thread = None
    # tentativo di coneessione al server, se fallisce annulliamo tutto
    try:
        client_socket.connect(addr)
        statusActive = True
        # invio del nome utente al server
        send_message(client_name)
        # avvio del thread di ascolto dei messaggi
        thread = Thread(target=receiver, )
        thread.start()
        return True
    except Exception as data:
        print("Errore di connessione")
        closeConnection()
    return False

def closeConnection():
    """
    Chiude la connessione con il server del socket client_socket
    """
    global statusActive
    global client_socket
    # Terminiamo solo se risulta essere ancora attivo
    if statusActive:
        statusActive = False
        try:
            client_socket.close()
            client_socket = None
        except OSError:
            print("Errore nella chiusura della connessione")
        notifyClosedConnection()

def receiver():
    """
    Ascolta e riceve i messaggi dal server sul socket client_socket
    """
    global client_socket
    # Usiamo il timeout per far si che non resti bloccato in attesa di ricevere messaggi
    # se il socket viene chiuso statusActive viene posto a False, terminando il ciclo e il thread
    client_socket.settimeout(1.0)
    while statusActive:
        try:
            msg = client_socket.recv(BUFFSIZE).decode("utf8")
            if msg != QUIT_COMMAND:
                notifyIncomingMsg(msg)
            else:
                closeConnection()
        except TimeoutError:
            continue
        except OSError:
            closeConnection()
            break

def send_message(msg):
    """
    Invio di un messaggio (msg) al server tramite client_socket
    """
    global client_socket
    # In caso di errore o di messaggio corrispondente al comando di uscita terminiamo la connessione
    if statusActive:
        try:
            client_socket.send(bytes(msg, "utf8"))
        except OSError:
            closeConnection()
        if msg == QUIT_COMMAND:
            closeConnection()

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

def signal_handler(signal, frame):
    """
    Termina l'esecuzione del client (usato dal comando Ctrl+C)
    """
    if statusActive:
        closeConnection()
    sys.exit(0)

# Se lanciato come script, avvia il client come solo "ascoltatore"
# E' necessario commentare queste ultime righe di script se si desidera creare l'eseguibile
if __name__ == "__main__":
    connect(ADDR, "ServerListener")
    # avvia un loop per mantenere attivo il main thread in ascolto per il segnale di terminazione
    signal.signal(signal.SIGINT, signal_handler)
    while statusActive:
       time.sleep(1)
