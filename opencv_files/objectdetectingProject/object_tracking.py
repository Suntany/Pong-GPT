import cv2

#tracker = cv2.TrackerKCF_create()  #KCF 알고리즘
tracker = cv2.TrackerCSRT_create()  #CSRT 알고리즘

video = cv2.VideoCapture('street.mp4')  #mpt 불러오기
ok, frame = video.read() #read first frame

bbox = cv2.selectROI(frame) #트래킹하려는 객체를 선택
#print(bbox)

ok = tracker.init(frame, bbox)
#print(ok)

while True: #영상 재생 동안
    ok, frame = video.read()
    #print(ok)

    if not ok:
        break
    ok, bbox = tracker.update(frame) #frame이 바뀔 때마다 bbox를 업데이트한다
    #print(bbox)
    #print(ok)

    if ok:
        (x, y, w, h) = [int(v) for v in bbox]  #변수에 대입
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2, 1)
        # (0,25,0): 색상, 2: 두께
    else:
        cv2.putText(frame, 'Error', (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow('Tracking', frame)
    if cv2.waitKey(1) & 0XFF == 27: # ESC
        break
