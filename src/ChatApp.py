import tkinter as tkt
import ChatServer
import ChatClient

def send_message(event=None):
    msg = msg_text.get()
    msg_text.set("")
    ChatClient.send_message(client_socket, msg)

class ChatClientListener:
    def updateMessages(msg):
        msg_list.insert(tkt.END, msg)

    def closedConnection():
        msg_list.insert(tkt.END, "Connessione chiusa")
        msg_list.insert(tkt.END, "Per chiudere la finestra, premi il tasto 'X'")
        receiver_Thred.join()
        finestra.quit()

def on_closing():
    msg_text.set(ChatClient.QUIT_COMMAND)
    send_message()

finestra = tkt.Tk()
finestra.title("Chatrooms")

msg_frame = tkt.Frame(finestra)

scrollbar = tkt.Scrollbar(msg_frame)
msg_list = tkt.Listbox(msg_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
msg_frame.pack()

msg_text = tkt.StringVar()
entry_field = tkt.Entry(finestra, textvariable=msg_text)
entry_field.bind("<Return>", send_message)
entry_field.pack()

send_button = tkt.Button(finestra, text="Invio", command=send_message)
send_button.pack()

finestra.protocol("WM_DELETE_WINDOW", on_closing)

receiver_Thred, client_socket = ChatClient.connect(ChatClient.ADDR, "SERVER")
ChatClient.addListener(ChatClientListener)

if receiver_Thred is not None:
    tkt.mainloop()
