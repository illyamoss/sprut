from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


class EndToEndEncryption:
    def __init__(self, rsa_key_size: int) -> None:
        self.__rsa_key_size = rsa_key_size

        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.__rsa_key_size,
            backend=default_backend()
        )
        self.__public_key = self.__private_key.public_key()

        self.__public_key_from_peer: rsa.RSAPublicKey

    def get_max_rsa_chipher_size(self) -> int:
        """ Get a maximum data size for encryption/decryption using RSA. """
        return (self.__rsa_key_size + 7) // 8

    def get_public_key(self) -> bytes:
        return self.__public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def set_public_key_from_peer(self, key: bytes) -> None:
        self.__public_key_from_peer = serialization.load_der_public_key(
            key, backend=default_backend()
        )

    def encrypt(self, plaintext: bytes) -> bytes:
        return self.__public_key_from_peer.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))

    def decrypt(self, encrypted_data: bytes) -> bytes:
        return self.__private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
