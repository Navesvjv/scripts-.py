import socket

HEADER = 20
PORT = 5056
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.20.6"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    
    client.send(send_length)
    client.send(message)

    if msg != DISCONNECT_MESSAGE:
        resp_len = client.recv(HEADER).decode(FORMAT)
        resp_len = int(resp_len)
        
        response = client.recv(resp_len).decode(FORMAT)
        print(response)

while True:
    command = input('Commando: ')
    if command == 'exit':
        send(DISCONNECT_MESSAGE)
        break    
    send(command)
