import tkinter as tkt
import ChatServer
import ChatClient

msg_text = None
msg_list = None
app = None

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
        global app
        """
        Termina l'esecuzione dell'applicazione
        """
        msg_list.insert(tkt.END, "Connessione chiusa")
        msg_list.insert(tkt.END, "Per chiudere la finestra, premi il tasto 'X'")
        app.quit()

def on_closing():
    """
    A chiusura dell'applicazione invia il comando di disconnessione
    """
    msg_text.set(ChatClient.QUIT_COMMAND)
    send_message()

class ChatRoom(tkt.Frame):
    def __init__(self, parent, controller): 
        global msg_text
        global msg_list
        global app

        tkt.Frame.__init__(self, parent)

        # Crea la lista dei messaggi con scrollbar
        scrollbar = tkt.Scrollbar(self)
        msg_list = tkt.Listbox(self, height=15, width=50, yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
        msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
        # Crea il field in cui poter scrivere i messaggi da inviare
        msg_text = tkt.StringVar()
        entry_field = tkt.Entry(self, textvariable=msg_text)
        entry_field.bind("<Return>", send_message)
        entry_field.pack()
        # Crea il pulsante per inviare i messaggi
        send_button = tkt.Button(self, text="Invio", command=send_message)
        send_button.pack()

class ChatRoom2(tkt.Frame):
    def __init__(self, parent, controller): 
        global msg_text
        global msg_list

        tkt.Frame.__init__(self, parent)

        label = tkt.Label(self, text ="Page 2")
        label.pack()

class tkinterApp(tkt.Tk):
    # __init__ function for class tkinterApp 
    def __init__(self, *args, **kwargs): 
        # __init__ function for class Tk
        tkt.Tk.__init__(self, *args, **kwargs)
        self.title("Chatroom")
        # creating a container
        container = tkt.Frame(self) 
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        # initializing frames to an empty array
        self.frames = {} 
        # iterating through a tuple consisting
        # of the different page layouts
        for F in (ChatRoom, ChatRoom2):
            frame = F(container, self)
            # initializing frame of that object from
            # startpage, page1, page2 respectively with 
            # for loop
            self.frames[F] = frame 
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(ChatRoom)

	# to display the current frame passed as
	# parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Crea la connessione al server
app = tkinterApp()
receiver_Thred, client_socket = ChatClient.connect(ChatClient.ADDR, "SERVER")
ChatClient.addListener(ChatClientListener)
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
