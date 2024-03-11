import thread
import time

hilo = thread.thread()

x = 0
while True:
    print(f"CORE: {x}")
    x += 1
    time.sleep(1)