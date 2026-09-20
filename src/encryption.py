import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def generate_private_rsa_key():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    return private_key


def serialize_public_key(private_key):
    public_key = private_key.public_key()

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return public_key_bytes


class Encryption:
    def __init__(self, key: bytes) -> None:
        if len(key) not in (16, 24, 32):
            raise ValueError("AES key must be 16, 24, or 32 bytes")

        self.aes = AESGCM(key)

    def encrypt(self, message: str):
        nonce = os.urandom(12)

        ciphertext = self.aes.encrypt(nonce, message.encode("utf-8"), None)

        return nonce + ciphertext

    def decrypt(self, data: bytes):
        nonce = data[:12]
        ciphertext = data[12:]

        plaintext = self.aes.decrypt(nonce, ciphertext, None)

        return plaintext.decode("utf-8")
