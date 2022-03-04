import pytest
import requests

from sprut.utils import (
    generate_passphrase, get_public_ip, split_string_by_bytes
)


@pytest.mark.parametrize(
    "passphrase_words_count", [1, 3, 5, 6, 7, 9, 10, 20, 50],
)
def test_generate_passphrase(passphrase_words_count) -> None:
    random_words = generate_passphrase(
        passphrase_words_count=passphrase_words_count
    )

    assert len(random_words.split("-")) == passphrase_words_count


@pytest.mark.parametrize(
    "string, bytes_count, result", 
    [
        ("Hello", 1, ["H", "e", "l", "l", "o"]),
        ("Hello", 2, ["He", "ll", "o"]),
        ("Hello, world!", 6, ["Hello,", " world", "!"]),
        ("", 1, []),
        ("Hello, mother", -1, []),
    ],
)
def test_string_separation_by_bytes(
    string: str, bytes_count: int, result: list[str]
) -> None:
    assert split_string_by_bytes(string, bytes_count=bytes_count) == result
