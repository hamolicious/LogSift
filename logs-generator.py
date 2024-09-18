import time
import random
import string
import logging


def rand_num() -> float:
    num = random.random() * random.randint(0, 1000)
    return num


logs = [
    "useless log",
    "Error: some shit went wrong",
    f"this has done a total {rand_num()} of stuff and such",
]


while True:
    logging.info(random.choice(logs))
    time.sleep(random.randint(0, 3))
