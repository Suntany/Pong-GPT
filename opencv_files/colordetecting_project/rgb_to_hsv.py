import numpy as np
import cv2


color = [255, 0, 0] #blue
pixel = np.uint8([[color]]) #한 픽셀

hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV) #cvtcolor 함수로 hsv 값 대입
hsv = hsv[0][0]


print("bgr: ", color)
print("hsv: ", hsv)