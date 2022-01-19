import string
import random

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


RSA_KEY_SIZE = 2048
PASSPHRASE_LENGTH = 10


def generate_passphrase():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(PASSPHRASE_LENGTH)) 


class EndToEndEncryption:
    def __init__(
        self, 
        private_key: rsa.RSAPrivateKey = None, 
        public_key: rsa.RSAPublicKey = None
    ) -> None:
        self.__private_key = private_key
        self.__public_key = public_key

    @classmethod
    def generate_keys(cls):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=RSA_KEY_SIZE,
            backend=default_backend())
        public_key = private_key.public_key()

        return cls(private_key, public_key)

    @classmethod
    def load_keys_from_bytes(
        cls, 
        private_key_bytes: bytes = None, 
        public_key_bytes: bytes = None
    ):
        if private_key_bytes is None:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=RSA_KEY_SIZE,
                backend=default_backend())
        else:
            private_key = serialization.load_pem_private_key(
                private_key_bytes,
                password=None,
                backend=default_backend())

        if public_key_bytes is None:
            public_key = private_key.public_key()
        else: 
            public_key = serialization.load_der_public_key(
                public_key_bytes,
                backend=default_backend())

        return cls(private_key, public_key)


    def encrypt_str(self, string: str) -> bytes:
        return self.__public_key.encrypt(
            string.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))

    def decrypt_str(self, encrypted_str: bytes) -> bytes:
        return self.__private_key.decrypt(
            encrypted_str,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
