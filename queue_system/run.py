import random
from time import sleep

class Message:
    def __init__(self, body: str, webhook: str):
        self.body = body
        self.webhook = webhook

queue : list[Message] = []
i = 0
while True:
    print(f"Run {i}")
    sleep(random.randint(2, 5))
    i += 1
    if i > 100:
        break
