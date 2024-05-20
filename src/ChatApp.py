import tkinter as tkt
import ChatServer
import ChatClient

msg_text = None
msg_list = None
app = None
isConnected = False
isHosting = False
name = None

def send_message(event=None):
    """
    Invia un messaggio leggendo il contenuto da msg_text
    """
    msg = msg_text.get()
    msg_text.set("")
    ChatClient.send_message(msg)

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
        global isConnected
        """
        Termina l'esecuzione dell'applicazione
        """
        isConnected = False
        msg_list.insert(tkt.END, "Connessione chiusa")
        msg_list.insert(tkt.END, "Per chiudere la finestra, premi il tasto 'X'")

def on_closing():
    """
    A chiusura dell'applicazione invia il comando di disconnessione
    """
    global msg_text
    global isConnected
    global isHosting
    global app

    if isConnected:
        isConnected = False
        msg_text.set(ChatClient.QUIT_COMMAND)
        send_message()
    if isHosting:
        isHosting = False
        ChatServer.closeServer()
    app.quit()

def establish_connection(addr = ChatClient.ADDR):
    global isConnected
    global name

    host, port = addr
    if host == "":
        host = ChatClient.HOST
    if port == "":
        port = ChatClient.PORT
    else:
        port = int(port)
    isConnected = ChatClient.connect((host, port), name.get())
    ChatClient.addListener(ChatClientListener)
    if isConnected:
        app.show_frame(ChatRoom)

def host_server():
    global isHosting
    isHosting = True
    addr = ChatServer.start_server(ChatServer.ADDR)
    if addr is not None:
        msg_list.insert(tkt.END, "Server avviato all'indirizzo " + addr[0] + ":" + str(addr[1]))
        establish_connection()

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

class Homepage(tkt.Frame):
    def __init__(self, parent, controller): 
        global name
        tkt.Frame.__init__(self, parent)
        # Titolo della pagina
        label = tkt.Label(self, text ="Chatroom")
        label.pack()
        # Crea i pulsanti per hostare o connettersi ad una chat
        host_button = tkt.Button(self, text="Host chat", command = lambda : host_server())
        host_button.pack()
        connect_button = tkt.Button(self, text="Connect to chat", command = lambda : controller.show_frame(ConnectPage))
        connect_button.pack()
        # Crea il campo per inserire il proprio nome
        label = tkt.Label(self, text ="Come ti chiami?")
        label.pack()
        name = tkt.StringVar()
        name_entry = tkt.Entry(self, textvariable=name)
        name_entry.pack()

class ConnectPage(tkt.Frame):
    def __init__(self, parent, controller): 
        tkt.Frame.__init__(self, parent)
        # Titolo della pagina
        label = tkt.Label(self, text ="ConnectPage")
        label.pack()
        # Crea il campo per inserire l'indirizzo del server
        label = tkt.Label(self, text ="Inserisci l'indirizzo del server:")
        label.pack()
        host_address = tkt.StringVar()
        host_entry = tkt.Entry(self, textvariable=host_address)
        host_entry.pack()
        label = tkt.Label(self, text ="Inserisci la porta del server:")
        label.pack()
        port_address = tkt.StringVar()
        port_entry = tkt.Entry(self, textvariable=port_address)
        port_entry.pack()
        # Crea il pulsante per connettersi al server
        connect_button = tkt.Button(self, text="Connetti", command = lambda : establish_connection((host_address.get(), port_address.get())))
        connect_button.pack()

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
        for F in (ChatRoom, Homepage, ConnectPage):
            frame = F(container, self)
            # initializing frame of that object from
            # startpage, page1, page2 respectively with 
            # for loop
            self.frames[F] = frame 
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(Homepage)

	# to display the current frame passed as
	# parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Crea la connessione al server
app = tkinterApp()
app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
