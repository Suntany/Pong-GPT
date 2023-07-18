import customtkinter
import time
import cv2
from imutils.video import VideoStream


# vs = VideoStream(src=1).start()

time.sleep(2.0)


def test_fuction():
    print("hello")


test_fuction()


########## GUI ##########

app = customtkinter.CTk()
app.title("pongGPT v1.0")
app.geometry("800x400")

# 타이틀
title_label = customtkinter.CTkLabel(
    app, text="PongGPT GUI System", fg_color="transparent", font=("System", 24)
)
title_label.grid(row=0, column=0, padx=20, pady=10)

# OpenCV 시작
start_opencv = customtkinter.CTkButton(app, text="Start OpenCV", command=test_fuction)
start_opencv.grid(row=1, column=0, padx=0, pady=0)

# 현재 좌표
current_xy = customtkinter.CTkLabel(
    app, text="Current XY", fg_color="transparent", font=("System", 18)
)
current_xy.grid(row=2, column=0, padx=20, pady=10)

current_xy_textbox = customtkinter.CTkTextbox(app, height=20, state="normal")
current_xy_textbox.insert("0.0", "hello")
current_xy_textbox.grid(row=2, column=0, padx=20, pady=10)

app.mainloop()
