
from security.key_manager import KeyManager


#It owns the cryptography
# THis class would be having Key exchange, masking, encryption, protocol state
class CLientProtocol:
    def __init__(self,partition_id):
        self.partition_id = partition_id
        self.key_manager = KeyManager()
        self.peer_public_key = None
        self.shared_secret = None
        print(f"[Protocol] Initialized CLient: {partition_id}")
    
    def generate_public_key(self):
        return self.key_manager.get_public_key_bytes()
    
    def print_public_key(self):
        key = self.generate_public_key()
        print(f"\n ================= CLIENT PUBLIC KEY ===================")
        print(f"Partition : {self.partition_id} with Public Key: {key.hex()}")
        return key
    
    def receive_peer_public_key(self,peer_node,public_key):
        self.peer_node = peer_node
        self.peer_public_key = public_key

        print(f"[Client]: {self.partition_id} received public key from Peer: {peer_node}")

    def compute_shared_secret(self):
        if self.peer_public_key is None:
            raise RuntimeError("Peer Public key is not received")
        
        self.shared_secret = self.key_manager.compute_shared_secret(self.peer_public_key)
        return self.shared_secret

    def print_shared_secret(self):
        secret = self.compute_shared_secret()
        print()
        print(f"[Client]: {self.partition_id} SHared Secret")
        print(secret.hex())
        return secret
    