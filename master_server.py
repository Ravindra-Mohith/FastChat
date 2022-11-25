import socket
import pickle
import psycopg2, threading, sys, select

HEADERSIZE = 10
HEADER_LENGTH = 10

conn = psycopg2.connect(
    database="fastchat",
    user="postgres",
    password="sandy@08",
    host="127.0.0.1",
    port="5432",
)
cursor = conn.cursor()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostname(), 9999))
server_socket.listen()
sockets_list = [server_socket]
clients = {}


def recieveMessage(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        # if message_header is null
        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {
            "header": message_header,
            "data": client_socket.recv(message_length),
        }

    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for socket in read_sockets:
        if socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = recieveMessage(client_socket)

            # if socket got disconnected:
            if user is False:
                continue

            # online sockets appending the current socket
            sockets_list.append(client_socket)

            clients[client_socket] = user

            print(
                f"Accepted a new connection from {client_address[0]}:{client_address[1]}. username : {user['data'].decode('utf-8')}"
            )

        else:
            message_recieved = recieveMessage(socket)

            if message_recieved is False:
                print(
                    f"Closed connection from {clients[socket]['data'].decode('utf-8')}"
                )
                sockets_list.remove(socket)
                del clients[socket]
                continue

            user = clients[socket]
            print(
                f"Recieved data from {user['data'].decode('utf-8')}: {message_recieved['data'].decode('utf-8')}"
            )

            message = recieveMessage(socket)

            for client_socket in clients:
                if client_socket != socket:
                    client_socket.send(
                        message_recieved["header"]
                        + message_recieved["data"]
                        + message["header"]
                        + message["data"]
                    )

    for socket in exception_sockets:
        sockets_list.remove(socket)
        del clients[socket]
