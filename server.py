import socket 
import threading
import subprocess

HEADER = 20
PORT = 5056
SERVER = '192.168.20.6'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr[0]}:{addr[1]} connected.")

    while True:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                break

            output = subprocess.getoutput(msg).encode(FORMAT)

            output_len = len(output)
            resp_len = str(output_len).encode(FORMAT)
            resp_len += b' ' * (HEADER - len(resp_len))

            conn.send(resp_len)
            conn.send(output)

    print(f'[CLOSE CONNECTION] {addr[0]}:{addr[1]} closed.')
    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


print("[STARTING] server is starting...")
start()
