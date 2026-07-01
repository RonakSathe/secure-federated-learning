from dataclasses import dataclass,field
import time
from .session import ProtocolSession
#Responsibility  is to collect Public keys, store them and DIstribute them whever needed
@dataclass
class PublicKeyPacket:
    session_id: str
    node_id: str
    public_key: bytes
    protocol_version: int = 1
    timestamp: float = field(default_factory=lambda: time.time)

class KeyRegistry:
    
    def register_key(self,session:ProtocolSession,packet:PublicKeyPacket):
        session.public_keys[packet.node_id] = packet
        print(f"Registered public key for node: {packet.node_id}")
    
    def get_public_key(self,session:ProtocolSession,node_id:str):
        return session.public_keys.get(node_id)
    
    def get_all(self,session:ProtocolSession):
        return session.public_keys
