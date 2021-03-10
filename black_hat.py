import os
import sys
import getopt
import socket
import platform
import threading
import subprocess


HEADER = 20
IP = ''
PORT = 0
FORMAT = 'utf-8'
LISTEN = False
ITERAVEL = False
DISCONNECT_MESSAGE = "!DISCONNECT"


def sysop():
    if platform.system() == 'Windows':
        return 'W', 'cls'
    elif platform.system() == 'Linux':
        return 'L', 'clear'
    else:
        return 'D', '' # Desconhecido


def clear():
    os.system(sysop()[1])


def help(msg):
    clear()
    if msg != '':
        print(f'\n{msg}\n')
    print('\n============================= Black Hat =============================\n')
    print('    -h  --help                   -> Help')
    print('    -k  --sizeheader             -> Tamanho do primeiro pacote (HEADER)')
    print('    -a  --address                -> [IP]:[PORT] server / [IP]:[PORT] target')
    print('    -f  --format                 -> Formato encode/decode\n')
    print('[SERVIDOR]')
    print('    -l  --listen                 -> Escuta em [IP]:[PORT]\n')
    print('[CLIENTE]')
    print('    -i  --iteravel               -> Modo iteravel (cliente pode digitar mais de um comando)\n\n')
    sys.exit(0)
    

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
        

def start_server():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((IP, PORT))
    servidor.listen()
    print(f"[SERVER] listening on {IP}:{PORT}")
    while True:
        conn, addr = servidor.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


def send_client_to_server(msg, client):
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


def start_client():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((IP, PORT))

    while ITERAVEL:
        command = input('Commando: ')
        if command == 'exit':
            send_client_to_server(DISCONNECT_MESSAGE, client)
            break    
        send_client_to_server(command, cliente)


def main():

    global HEADER
    global IP
    global PORT
    global FORMAT
    global LISTEN
    global ITERAVEL
    global DISCONNECT_MESSAGE

    if len(sys.argv[1:]) == 0:  # Se não foi passado argumento, então exibe "Help"
        help('')

    try: 
        opts, args = getopt.getopt(sys.argv[1:], 'hk:a:f:li', ['help', 'sizeheader=', 'address=', 'format=', 'listen=', 'iteravel='])
    except getopt.GetoptError as err:
        print(str(err))
        help('')

    for o, a in opts:
        if o in ('-h', '--help'):
            help('')
        elif o in ('-k', '--sizeheader'):
            HEADER = a
        elif o in ('-a', '--address'):
            IP, PORT = a.split(sep=':')
            PORT = int(PORT)
        elif o in ('-f', '--format'):
            FORMAT = a
        elif o in ('-l', '--listen'):
            LISTEN = True
        elif o in ('-i', '--iteravel'):
            ITERAVEL = True
        else:
            assert False, 'Opção não tratada'

    if LISTEN and not ITERAVEL:
        start_server()
    elif not LISTEN and ITERAVEL:
        start_client()
    else:
        help('Não foi passado cliente ou servidor no comando.')


main()