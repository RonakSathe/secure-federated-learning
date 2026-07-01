from dataclasses import dataclass, field
import time

@dataclass
class PublicKeyPacket:
    session_id: str
    node_id: str
    public_key: bytes
    protocol_version: int = 1
    timestamp: float = field(default_factory=lambda: time.time)

    

@dataclass
class PeerPacket:
    session_id: str
    sender_node: int
    receiver_node: int
    peer_node: int
    peer_public_key: bytes
    timestamp: float = field(default_factory=time.time)
    