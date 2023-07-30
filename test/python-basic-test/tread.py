import threading
import time


def mythread():
    print("[Sub] start")
    for i in range(10):
        print("[Sub]", end="")
        print(i * 0.5)
        time.sleep(0.5)


newthread = threading.Thread(target=mythread, daemon=False)

print("[Main] start")
print(time.time())
time.sleep(1)
print(time.time())
for i in range(10):
    print("[Main]", end="")
    print(i)
    time.sleep(1)

newthread.start()
