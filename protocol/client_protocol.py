
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
    
