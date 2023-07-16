# import the necessary packages

# 콜렉션 모듈에서 deque라는 데이터 처리 함수
from collections import deque
#
from imutils.video import VideoStream
# numpy 모듈 임포트
import numpy as np
# argparse 모듈 임포트 (파이썬 스크립트를 명령 프롬프트에서 실행할 때 명령행 인자를 파싱할 수 있게 한다)
import argparse
# OpenCV 모듈 임포트
import cv2
# imutils 모듈 임포트 (이미지 프로세싱 관련된 유용한 기능들 있다)
import imutils
# time 모듈 임포트
import time

# construct the argument parse and parse the arguments

# parser를 만든다 이름은 ap
ap = argparse.ArgumentParser()

# add_argument 메서드로 받아들일 인수를 추가해나간다
# -v 로 비디오 파일을 선택해서 재생할 수 있다.
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")

# -b 로 최대 버퍼 사이즈를 지정할 수 있다 기본은 64
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")

args = vars(ap.parse_args())

# define the lower and upper boundaries of the "Orange"
# ball in the HSV color space, then initialize the
# list of tracked points
orangeLower = (17, 255, 150)
orangeUpper = (34, 255, 255)
pts = deque(maxlen=args["buffer"])
# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	vs = VideoStream(src=0).start()
# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])
# allow the camera or video file to warm up
time.sleep(2.0)

# keep looping
while True:
	# grab the current frame
	frame = vs.read()
	# handle the frame from VideoCapture or VideoStream
	frame = frame[1] if args.get("video", False) else frame
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if frame is None:
		break
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
	# construct a mask for the color "orange", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, orangeLower, orangeUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
			print(center)
	# update the points queue
	pts.appendleft(center)
	# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()
# otherwise, release the camera
else:
	vs.release()
# close all windows
cv2.destroyAllWindows()