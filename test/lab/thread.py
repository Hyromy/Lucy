import threading
import time
import random

def suma():
    while True:
        n1 = random.randint(1, 10)
        n2 = random.randint(1, 10)
        print(f"THREAD: ({n1 + n2})")
        time.sleep(1.333)

class thread:
    def __init__(self):
        hilo = threading.Thread(target = suma)
        hilo.daemon = True
        hilo.start()