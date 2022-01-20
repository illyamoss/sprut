from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


RSA_KEY_SIZE = 2048


class EndToEndEncryption:
    def __init__(
        self, 
        private_key: rsa.RSAPrivateKey = None, 
        public_key: rsa.RSAPublicKey = None
    ) -> None:
        self.__private_key = private_key
        self.__public_key = public_key

        self.__public_key_from_peer: rsa.RSAPublicKey

    @classmethod
    def generate_keys(cls):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=RSA_KEY_SIZE,
            backend=default_backend())
        public_key = private_key.public_key()

        return cls(private_key, public_key)

    @property.getter
    def public_key(self) -> bytes:
        return self.__public_key

    @property.setter
    def public_key_from_peer(self, key: bytes) -> None:
        self.__public_key_from_peer = serialization.load_der_public_key(
                key,
                backend=default_backend())

    def encrypt_str(self, string: str) -> bytes:
        return self.__public_key_from_peer.encrypt(
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
