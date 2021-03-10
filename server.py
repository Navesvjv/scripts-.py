import os
import sys
import getopt
import socket
import platform
import threading
import subprocess


HEADER = 20
PORT = 5056
SERVER = '192.168.20.6'
TARGET = '192.168.20.6'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
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


def help():
    clear()
    print('\n============================= Black Hat =============================\n')
    print('    -h  --help                   -> Help')
    print('    -k  --size                   -> Tamanho do primeiro pacote (HEADER)\n')
    print('[SERVIDOR]')
    print('    -l  --listen                 -> Escuta em [SERVER]:[PORT]')
    print('    -s  --ipserver               -> IP do servidor')
    print('    -p  --port                   -> Porta de acesso no servidor\n')
    print('[CLIENTE]')
    print('    -c  --command                -> Comando a ser executando no servidor')
    print('    -t  --target                 -> Ip do target (servidor)')
    print('\n')
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
        

def start():
    SERVER.listen()
    print(f"[LISTENING] SERVER is listening on {SERVER}")
    while True:
        conn, addr = SERVER.accept()
        thread = threading.Thread(SERVER=handle_client, args=(conn, addr))
        thread.start()


def main():
    if len(sys.argv[1:]) == 0:  # Se não foi passado argumento, então exibe "Help"
        help()

    try: 
        opts, args = getopt.getopt(sys.argv[1:], 'hls:p:c:t:')  # Pega os argumentos passados no comando
    except getopt.GetoptError as err:
        print(str(err))
        help()

    for o, a in opts:
        if o in ("-h", "--help"):
            help()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Opção não tratada"

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind(ADDR)

    print("[STARTING] SERVER is starting...")
    start()

main()