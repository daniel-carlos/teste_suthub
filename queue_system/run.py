import random
from time import sleep

i = 0
while i < 100:
    print(f"Run {i}")
    sleep(random.randint(2, 5))
    i += 1
    if i > 100:
        break
