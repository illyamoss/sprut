from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


MAX_RSA_ENCRYPTION_SIZE = 190


class EndToEndEncryption:
    def __init__(
        self,
        rsa_key_size: int,
        private_key: rsa.RSAPrivateKey | bytes,
        public_key: rsa.RSAPublicKey | bytes,
    ) -> None:
        self.__rsa_key_size = rsa_key_size

        if isinstance(private_key, bytes) and isinstance(public_key, bytes):
            self.__private_key = serialization.load_der_private_key(
                private_key, backend=default_backend(), password=None
            )
            self.__public_key = serialization.load_der_public_key(
                public_key, backend=default_backend()
            )

        elif isinstance(private_key, rsa.RSAPrivateKey) and isinstance(
            public_key, rsa.RSAPublicKey
        ):
            self.__private_key = private_key
            self.__public_key = public_key

        else:
            raise TypeError("You passed a keys type in an unsupported type.")

    @classmethod
    def generate_keys(cls, rsa_key_size):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=rsa_key_size,
            backend=default_backend(),
        )
        public_key = private_key.public_key()

        return cls(rsa_key_size, private_key, public_key)

    @property
    def public_key(self) -> bytes:
        return self.__public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    @public_key.setter
    def public_key(self, key: bytes):
        self.__public_key = serialization.load_der_public_key(
            key, backend=default_backend()
        )

    def get_rsa_key_size(self) -> int:
        """RSA key size in bytes"""
        return (self.__rsa_key_size + 7) // 8

    def encrypt(self, plaintext: bytes) -> bytes:
        return self.__public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def decrypt(self, encrypted_data: bytes) -> bytes:
        return self.__private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
