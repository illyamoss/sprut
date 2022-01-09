import string
import random


PASSPHRASE_SIZE = 10


def generate_passphrase():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(PASSPHRASE_SIZE)) 
