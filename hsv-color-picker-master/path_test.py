import cv2
import numpy as np
 
path = 'C:/Users/송환진/Downloads/hsv-color-picker-master'
img_name = 'ball.jpg'
full_path = path + '/' +img_name
 
img_array = np.fromfile(full_path, np.uint8)
img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

if img is not None:
  cv2.imshow('IMG', img)      # 읽은 이미지를 화면에 표시      --- ③
  cv2.waitKey()               # 키가 입력될 때 까지 대기      --- ④
  cv2.destroyAllWindows()     # 창 모두 닫기            --- ⑤
else:
    print('No image file.')