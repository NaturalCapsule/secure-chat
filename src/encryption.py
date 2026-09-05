import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


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
