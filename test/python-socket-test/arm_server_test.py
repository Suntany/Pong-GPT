import time
import threading
import socket


print("########### arm server test ############")

# TCP/IP 소켓통신
host = "127.0.0.1"
port = 10000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()
print("Connection Ready...")

# client
client_arm = None


# 로봇팔 값 전달
def arm_send(client_arm, fin_eta, fin_angle):
    try:
        message = "{0},{1}".format(fin_eta, fin_angle)
        client_arm.send(message.encode(encoding="utf-8"))
    except:
        client_arm.close()


# 클라이언트를 받음
client, address = server.accept()
print("Connected with {}".format(str(address)))
check_token = client.recv(1).decode()
if check_token == "r":
    print("Arm Connected!")
    client_arm = client
else:
    print("Connection Error")
    exit()

while True:
    print("Enter FINAL_ETA")
    FINAL_ETA = int(input())

    print("Enter FINAL_ANGLE")
    FINAL_ANGLE = float(input())

    # 로봇팔 송신 쓰레드
    arm_tr = threading.Thread(
        target=arm_send,
        args=(client_arm, FINAL_ETA, FINAL_ANGLE),
    )
    arm_tr.start()
