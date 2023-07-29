import cv2

img_color = cv2.imread('/Users/hwan_jin/Downloads/opencv_files/colordetecting_project/1.jpg') #이미지 파일 읽어오기
height,width = img_color.shape[:2] #이미지의 행, 열 개수

img_hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV) #hsv로 변환


lower_blue = (120-10, 30, 30) #하한값
upper_blue = (120+10, 255, 255) #상한값
img_mask = cv2.inRange(img_hsv, lower_blue, upper_blue)


img_result = cv2.bitwise_and(img_color, img_color, mask = img_mask)


cv2.imshow('img_color', img_color)
cv2.imshow('img_mask', img_mask)
cv2.imshow('img_result', img_result)


cv2.waitKey(0) #키보드 대기
cv2.destroyAllWindows() #사용 끝나면 종료