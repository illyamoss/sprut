import requests
import random


PASSPHRASE_WORDS_COUNT = 3
WORDS_LIST_TXT = "https://gist.githubusercontent.com/deekayen/4148741/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt"


def generate_passphrase() -> str:
    r  = requests.get(WORDS_LIST_TXT)
    words = r.content.decode().split()

    return "-".join([
        random.choice(words) for _ in range(PASSPHRASE_WORDS_COUNT)
    ])


def get_public_ip() -> str:
    return requests.get(
        "https://canhazip.com/"
    ).content.decode().removesuffix("\n")
