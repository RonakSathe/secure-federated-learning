from dataclasses import dataclass

@dataclass
class MaskingContext:
    shared_secret: bytes
    session_id: str
    round_number:int
    session_salt: bytes
    my_node_id: int
    peer_node_id: int