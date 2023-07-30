import threading
import time

myvalue = 0


def mythread():
    print("[Sub] start")
    for i in range(10):
        print("[Sub]", end="")
        print(i * 0.5)
        time.sleep(0.5)


def time_alarm(ETA):
    print("Line Activated / Detecting LOCK")
    print(time.time())
    time.sleep(ETA)
    print("Line Deactivated / Detecting UNLOCK")
    print(time.time())
    myvalue = 1
    print(myvalue)


newthread = threading.Thread(target=mythread, daemon=False)
timethread = threading.Thread(target=time_alarm, args=(0.001,), daemon=True)

timethread.start()

print("[Main] start")
print(2/3)
for i in range(10):
    print("[Main]", end="")
    print(i)
    time.sleep(1)
