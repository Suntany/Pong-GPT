import socket

# Setting network information
IP = '127.0.0.1'
PORT = 5050
SIZE = 1024
ADDRESS = (IP,PORT)

# Setting server socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind(ADDRESS) # address binding
    server_socket.listen() # ready to request client

    # infinite loop
    while True:
        client_socket, client_address = server_socket.accept() # return information of entered client (socket, address)
        msg = client_socket.recv(SIZE)
        print("[{}] message : {}".format(client_address,msg)) # 클라이언트가 보낸 메세지 출력

        client_socket.sendall("welcome!".encode()) # 클라이언트에게 응답

        client_socket.close() # 클라이언트 소켓 종료