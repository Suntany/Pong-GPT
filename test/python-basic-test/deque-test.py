from collections import deque
import time

mydeque = deque(maxlen=2)
print ("You make deque!")

time.sleep(1)

mydeque.append((1,2))
print(mydeque)
time.sleep(1)
if not mydeque[0] is None:
    print("happy")
print(len(mydeque))
mydeque.append((3,4))
print(mydeque)
time.sleep(1)
mydeque.append(3)
print(mydeque)
time.sleep(1)
mydeque.append(4)
print(mydeque)
time.sleep(1)

print(mydeque[0])
print(mydeque.popleft())
print(mydeque)

for i in range(4):
    print(i)

if (1,2) == (1,2):
    print("same")
