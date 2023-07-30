# 패키지 임포트
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import threading

##### 중요 환경 변수들 #####
VIDEO_SELECTION = 1  # 0번부터 카메라 포트 찾아서 1씩 올려보기
VIDEO_WIDTH = 1000  # 화면 가로 넓이
WIDTH_CUT = 160
CENTER_LINE = 340  # 세로 센터 라인
NET_LINE = 640  # 네트 라인

CATCH_FRAME = 4
MIN_GAP = 10

# 초기화 변수들
ball_in = False
line_on = False

RALLY_COUNT = 0
FINAL_MOVE = 0  # 단위 cm
FINAL_ETA = 0  # 단위 ms

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
    print("Line Activated / Detecting LOCK")
    time.sleep(ETA)
    line_on = False
    print("Line Deactivated / Detecting UNLOCK")
    line_xy.clear()
    temp_move.clear()
    temp_speed.clear()


# 쓰레드 생성


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
            #print(center)
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
                            np.sqrt(
                                (line_xy[0][0] - line_xy[1][0]) ** 2
                                + (line_xy[0][1] - line_xy[1][1]) ** 2
                            )
                            / ((time_xy[1] - time_xy[0]) * 1000)
                        )
                    )

        if len(temp_move) == CATCH_FRAME:
            #디버깅
            print(temp_speed)
            print(line_xy[1])

            temp_move.popleft()
            temp_speed.popleft()

            temp_move_sum = 0
            for i in range(CATCH_FRAME - 1):
                temp_move_sum += temp_move.popleft()
            FINAL_MOVE = int(temp_move_sum / (CATCH_FRAME - 1) * (152.5 / 680))

            temp_speed_sum = 0
            for i in range(CATCH_FRAME - 1):
                temp_speed_sum += temp_speed.popleft()
            FINAL_ETA = int(
                np.sqrt(
                    (line_xy[1][0] - FINAL_MOVE * (680 / 152.5)) ** 2
                    + (line_xy[1][1] - 1220) ** 2
                )
                / (temp_speed_sum / (CATCH_FRAME - 1))
            )

            print(
                "FINAL MOVE : {0}cm / FINAL ETA : {1}ms".format(FINAL_MOVE, FINAL_ETA)
            )
            line_on = True
        
            newline_act = threading.Thread(target=line_activator, args=(FINAL_ETA / 1000,), daemon=True)
            newline_act.start()


    # 트레킹 레드라인 코드
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

    # show the frame to our screen
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
    elif key == ord("r"):
        line_xy.clear()
        temp_move.clear()
        temp_speed.clear()
        line_on = False
        FINAL_MOVE = None
        FINAL_ETA = None


# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()
# otherwise, release the camera
else:
    vs.release()
# close all windows
cv2.destroyAllWindows()
