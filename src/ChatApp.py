import tkinter as tkt
import ChatServer
import ChatClient

def send_message(event=None):
    """
    Invia un messaggio leggendo il contenuto da msg_text
    """
    msg = msg_text.get()
    msg_text.set("")
    ChatClient.send_message(client_socket, msg)

class ChatClientListener:
    """
    Classe che si occupa di ricevere notifiche dal thread in ascolto sul server
    """
    def updateMessages(msg):
        """
        Aggiunge msg alla lista dei messaggi ricevuti
        """
        msg_list.insert(tkt.END, msg)

    def closedConnection():
        """
        Termina l'esecuzione dell'applicazione
        """
        msg_list.insert(tkt.END, "Connessione chiusa")
        msg_list.insert(tkt.END, "Per chiudere la finestra, premi il tasto 'X'")
        finestra.quit()

def on_closing():
    """
    A chiusura dell'applicazione invia il comando di disconnessione
    """
    msg_text.set(ChatClient.QUIT_COMMAND)
    send_message()

# Crea la finestra dell'applicazione
finestra = tkt.Tk()
finestra.title("Chatrooms")
# Crea il frame
msg_frame = tkt.Frame(finestra)
# Crea la lista dei messaggi con scrollbar
scrollbar = tkt.Scrollbar(msg_frame)
msg_list = tkt.Listbox(msg_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
msg_frame.pack()
# Crea il field in cui poter scrivere i messaggi da inviare
msg_text = tkt.StringVar()
entry_field = tkt.Entry(finestra, textvariable=msg_text)
entry_field.bind("<Return>", send_message)
entry_field.pack()
# Crea il pulsante per inviare i messaggi
send_button = tkt.Button(finestra, text="Invio", command=send_message)
send_button.pack()
# Effettua il binding tra la X della finestra e la funzione on_closing
finestra.protocol("WM_DELETE_WINDOW", on_closing)

# Crea la connessione al server
receiver_Thred, client_socket = ChatClient.connect(ChatClient.ADDR, "SERVER")
ChatClient.addListener(ChatClientListener)
# Se la connessione ha avuto successo avvia l'applicazione
if receiver_Thred is not None:
    tkt.mainloop()
