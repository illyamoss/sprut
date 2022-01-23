import pytest

from sprut.crypt import EndToEndEncryption

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def test_load_keys_raises() -> None:
    with pytest.raises(TypeError):
        EndToEndEncryption(
            rsa_key_size=2048,
            private_key="not a valid key",
            public_key="not a valid key",
        )


@pytest.mark.parametrize(
    "rsa_key_size, result", 
    [
        [512, 64], 
        [1024, 128], 
        [2048, 256],
    ],
)
def test_max_rsa_size(rsa_key_size: int, result: int) -> None:
    e2ee = EndToEndEncryption.generate_keys(rsa_key_size=rsa_key_size)

    assert e2ee.get_max_rsa_chipher_size() == result


def test_load_keys_from_bytes() -> None:
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_key = private_key.public_key()

    private_der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    EndToEndEncryption(
        rsa_key_size=2048, private_key=private_der, public_key=public_der
    )


def test_generate_keys() -> None:
    EndToEndEncryption.generate_keys(rsa_key_size=2048)


@pytest.mark.parametrize(
    "plaintext",
    [
        b"Hello, world!",
        b"We are super team",
        b"Sprut is the best file transfer=)",
        b'*."[]:;|,/',
    ],
)
def test_cryption(plaintext: bytes) -> None:
    e2ee = EndToEndEncryption.generate_keys(rsa_key_size=2048)
    encrypted_data = e2ee.encrypt(plaintext)
    decrypted_data = e2ee.decrypt(encrypted_data)

    assert decrypted_data == plaintext
