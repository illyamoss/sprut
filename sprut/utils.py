import requests
import random


WORDS_LIST_TXT = (
    "https://gist.githubusercontent.com/deekayen/4148741"
    "/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt"
)


def generate_passphrase(passphrase_words_count: int) -> str:
    r = requests.get(WORDS_LIST_TXT)
    words = r.content.decode().split()

    return "-".join(
        [
            # Words with the symbol ', create a problem
            # so we'll just replace it out.
            random.choice(words).replace("'", "")
            for _ in range(passphrase_words_count)
        ]
    )


def get_public_ip() -> str:
    return (
        requests.get("https://canhazip.com/")
        .content.decode()
        .removesuffix("\n")
    )


def split_string_by_bytes(s: str, bytes_count: int) -> list[str]:
    """A function that splits a string into N-byte particles"""
    return [s[i : i + bytes_count] for i in range(0, len(s), bytes_count)]
