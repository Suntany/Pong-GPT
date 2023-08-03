# 패키지 임포트
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import threading
import socket

print("########### Pong GPT V5 ############")

# TCP/IP 소켓통신
host = "127.0.0.1"
port = 10000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()
print("Connection Ready...")

# clients
client_actu = None
client_arm = None

# 두 명의 클라이언트를 받음
for i in range(2):
    if i == 1:
        print("Next Connection Waiting...")
    client, address = server.accept()
    print("Connected with {}".format(str(address)))
    check_token = client.recv(1).decode()
    if check_token == "a":
        print("Actuator Connected!")
        client_actu = client
    elif check_token == "r":
        print("Robot Arm Connected!")
        client_arm = client
    else:
        print("Connection Error")
        exit()


# 엑추에이터 값 전달
def actu_send(client_actu, fin_move, fin_eta):
    try:
        message = "{0},{1}".format(fin_move, fin_eta)
        client_actu.send(message.encode(encoding="utf-8"))

    except:
        client_actu.close()


# 로봇팔 값 전달
def arm_send(client_arm, fin_eta, fin_angle):
    try:
        message = "{0},{1}".format(fin_eta, fin_angle)
        client_arm.send(message.encode(encoding="utf-8"))
    except:
        client_arm.close()


##### 중요 환경 변수들 #####
VIDEO_SELECTION = 1  # 0번부터 카메라 포트 찾아서 1씩 올려보기
VIDEO_WIDTH = 1000  # 화면 가로 넓이
WIDTH_CUT = 160
CENTER_LINE = 340  # 세로 센터 라인
NET_LINE = 640  # 네트 라인

CATCH_FRAME = 3
MIN_GAP = 50
MOVE_FIX = 0.1
ETA_FIX = 120

# 초기화 변수들
line_on = False
FINAL_MOVE = 0  # 단위 cm
FINAL_ETA = 0  # 단위 ms
FINAL_ANGLE = 0  # 단위 tangent

# 주황색 탁구공 HSV 색 범위 지정 (창문쪽 형광등 두 개 키고 문쪽 형광등 한 개 껐을때 기준)
orangeLower = (1, 130, 240)
orangeUpper = (30, 255, 255)

# 파서 코딩 부분
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

# 데큐 생성
pts = deque(maxlen=args["buffer"])
line_xy = deque(maxlen=2)  # 단위 px
time_xy = deque(maxlen=2)  # 단위 s
temp_move = deque()  # 단위 px
temp_speed = deque()  # 단위 px/ms


# Line Activater 쓰레드 함수
def line_activator(ETA):
    global line_on
    line_on = True
    print("Line Activated / Detecting LOCK")
    time.sleep(ETA)
    line_on = False
    print("Line Deactivated / Detecting UNLOCK")
    line_xy.clear()
    time_xy.clear()
    temp_move.clear()
    temp_speed.clear()


# 비디오 스트리밍 시작
vs = VideoStream(src=VIDEO_SELECTION).start()
time.sleep(2.0)

# 프레임 단위 무한 루프 영역
while True:
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    if frame is None:
        break
    # 화면비 (680x750)
    frame = imutils.resize(frame, width=VIDEO_WIDTH)
    frame = frame[0:750, WIDTH_CUT : 1000 - WIDTH_CUT]
    # 영상처리
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, orangeLower, orangeUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cv2.imshow("mask", mask)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    # 감지 했을 경우 (center 좌표 계산됨)
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # 탁구 알고리즘
        if line_on == False:
            line_xy.append(center)
            time_xy.append(time.time())
            if len(line_xy) == 2:
                if line_xy[0][1] + MIN_GAP < line_xy[1][1]:
                    temp_move.append(
                        int(
                            (1220 - line_xy[0][1])
                            * (line_xy[0][0] - line_xy[1][0])
                            / (line_xy[0][1] - line_xy[1][1])
                            + line_xy[0][0]
                        )
                    )
                    temp_speed.append(
                        int(
                            (line_xy[1][1] - line_xy[0][1])
                            / ((time_xy[1] - time_xy[0]) * 1000)
                        )
                    )
                if line_xy[0][1] > line_xy[1][1]:
                    line_xy.clear()
                    time_xy.clear()


        if len(temp_move) == CATCH_FRAME:
            temp_move.popleft()
            temp_speed.popleft()

            # move 계산
            temp_move_sum = 0
            for i in range(CATCH_FRAME - 1):
                temp_move_sum += temp_move.popleft()
            FINAL_MOVE = int(temp_move_sum / (CATCH_FRAME - 1) * (152.5 / 680))
            if FINAL_MOVE < 76:
                FINAL_MOVE += int((76 - FINAL_MOVE) * MOVE_FIX)
            else:
                FINAL_MOVE -= int((FINAL_MOVE - 76) * MOVE_FIX)

            # ETA 계산
            temp_speed_sum = 0
            for i in range(CATCH_FRAME - 1):
                temp_speed_sum += temp_speed.popleft()
            FINAL_ETA = (
                int((1220 - line_xy[1][1]) / (temp_speed_sum / (CATCH_FRAME - 1)))
                + ETA_FIX
            )

            # [[치트키]] 고정 
            FINAL_ETA = 200

            # TANGENT 계산
            FINAL_ANGLE = (1220 - line_xy[1][1]) / (
                line_xy[1][0] - FINAL_MOVE * (680 / 152.5)
            )

            print(
                "FINAL MOVE : {0}cm / FINAL ETA : {1}ms / FINAL ANGLE : {2}".format(
                    FINAL_MOVE, FINAL_ETA, FINAL_ANGLE
                )
            )

            # 감지 대기 쓰레드
            lineact_tr = threading.Thread(
                target=line_activator, args=(FINAL_ETA / 1000,), daemon=True
            )
            lineact_tr.start()

            # 엑추에이터 송신 쓰레드
            actu_tr = threading.Thread(
                target=actu_send,
                args=(
                    client_actu,
                    FINAL_MOVE,
                    FINAL_ETA,
                ),
            )
            actu_tr.start()

            # 로봇팔 송신 쓰레드
            arm_tr = threading.Thread(
                target=arm_send,
                args=(client_arm, FINAL_ETA, FINAL_ANGLE),
            )
            arm_tr.start()

    # rgb 트레킹 레드라인 코드
    pts.appendleft(center)
    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # 화면 표시 선 코드
    # 중앙선
    cv2.line(frame, (CENTER_LINE, 0), (CENTER_LINE, NET_LINE), (255, 255, 255), 2)

    # 네트선
    cv2.line(frame, (0, NET_LINE), (VIDEO_WIDTH, NET_LINE), (255, 255, 255), 2)

    # 화면 띄우기
    cv2.imshow("Frame", frame)

    # q : 종료 r : 리셋
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("r"):
        line_xy.clear()
        time_xy.clear()
        temp_move.clear()
        temp_speed.clear()
        line_on = False
        FINAL_MOVE = None
        FINAL_ETA = None
        FINAL_ANGLE = None

if not args.get("video", False):
    vs.stop()
else:
    vs.release()

cv2.destroyAllWindows()
