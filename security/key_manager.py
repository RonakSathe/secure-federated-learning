from cryptography.hazmat.primitives.asymmetric.x25519 import(X25519PrivateKey,X25519PublicKey)
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

class KeyManager:
    """Hanldes X25519 key genenration and shared secret computation"""

    def __init__(self):
        self.private_key = X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
    
    def get_public_key_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=Encoding.Raw,
            format= PublicFormat.Raw,
        )
    
    def compute_shared_secret(self,peer_public_key_bytes: bytes) -> bytes:
        peer_public_key = X25519PublicKey.from_public_bytes(peer_public_key_bytes)
        shared_secret = self.private_key.exchange(peer_public_key)
        return shared_secret